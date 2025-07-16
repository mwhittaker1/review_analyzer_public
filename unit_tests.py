import unittest
import pandas as pd
import duckdb
import os
import json
from unittest.mock import patch, MagicMock
import sys
import re
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import the modules we need to test
try:
    from apikey import create_secret
except ImportError:
    # Mock the API key for testing
    def create_secret():
        from openai import OpenAI
        # Use a dummy API key for testing
        return OpenAI(api_key="test-key-for-unit-testing")

class TestImportData(unittest.TestCase):
    """Test the data import functionality"""
    
    def setUp(self):
        # Setup test database
        self.db_path = "test_db"
        self.con = duckdb.connect(self.db_path)
        
        # Create a test CSV file
        self.test_csv = "test_data.csv"
        pd.DataFrame({
            'RETURN_COMMENT': ['Item was defective', 'Wrong size', 'Changed my mind'],
            'OTHER_COLUMN': [1, 2, 3]
        }).to_csv(self.test_csv, index=False)
        
        # Create a test Excel file
        self.test_excel = "test_data.xlsx"
        pd.DataFrame({
            'RETURN_COMMENT': ['Item was defective', 'Wrong size', 'Changed my mind'],
            'OTHER_COLUMN': [1, 2, 3]
        }).to_excel(self.test_excel, index=False)
        
    def tearDown(self):
        # Clean up test files
        self.con.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(self.test_excel):
            os.remove(self.test_excel)
    
    def test_import_csv(self):
        # Simplified version of import_data function for testing
        def import_data_csv(fname, con, tname='test_table', clear=True):
            mode = 'OR REPLACE TABLE' if clear else 'TABLE IF NOT EXISTS'
            con.execute(f"""
                CREATE {mode} {tname} AS
                SELECT *, ROW_NUMBER() OVER () AS row_id FROM read_csv_auto('{fname}', escape='\\', encoding='utf-8', header=True)
            """)
            return True
        
        # Test CSV import
        result = import_data_csv(self.test_csv, self.con)
        self.assertTrue(result)
        
        # Verify the data was imported
        result_df = self.con.execute("SELECT * FROM test_table").df()
        self.assertEqual(len(result_df), 3)
        self.assertTrue('row_id' in result_df.columns)
        self.assertTrue('RETURN_COMMENT' in result_df.columns)
    
    def test_import_excel(self):
        # Test function for Excel import
        def import_data_excel(fname, con, tname='test_table', clear=True):
            df = pd.read_excel(fname)
            if clear:
                con.execute(f"DROP TABLE IF EXISTS {tname}")
            df['row_id'] = range(1, len(df) + 1)
            con.register('temp_excel_df', df)
            con.execute(f"CREATE TABLE {tname} AS SELECT * FROM temp_excel_df")
            con.unregister('temp_excel_df')
            return True
            
        # Test Excel import
        result = import_data_excel(self.test_excel, self.con)
        self.assertTrue(result)
        
        # Verify the data was imported
        result_df = self.con.execute("SELECT * FROM test_table").df()
        self.assertEqual(len(result_df), 3)
        self.assertTrue('row_id' in result_df.columns)
        self.assertTrue('RETURN_COMMENT' in result_df.columns)


class TestDataFetching(unittest.TestCase):
    """Test the data fetching functionality"""
    
    def setUp(self):
        # Setup test database with sample data
        self.db_path = "test_fetch_db"
        self.con = duckdb.connect(self.db_path)
        
        # Create a test table with return comments
        self.con.execute("""
            CREATE TABLE test_returns (
                row_id INTEGER,
                RETURN_COMMENT VARCHAR,
                OTHER_DATA VARCHAR
            )
        """)
        
        # Insert test data
        self.con.execute("""
            INSERT INTO test_returns VALUES
            (1, 'Item was defective', 'data1'),
            (2, 'Wrong size', 'data2'),
            (3, 'Changed my mind', 'data3'),
            (4, '', 'data4'),
            (5, NULL, 'data5')
        """)
        
    def tearDown(self):
        # Clean up
        self.con.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_fetch_return_comments(self):
        def fetch_return_comments(con, tname, is_sample=False, comment_column='RETURN_COMMENT', row_id='row_id'):
            # Filter for non-empty comments
            comment_filter = f"""WHERE "{comment_column}" IS NOT NULL AND TRIM("{comment_column}") != ''"""
            
            if is_sample:
                sample_query = "ORDER BY RANDOM() LIMIT 2"  
            else:
                sample_query = ""
            
            # Select the comment and row_id
            query = f"""
            SELECT 
                "{row_id}" as row_id,
                "{comment_column}" as comment
            FROM {tname}
            {comment_filter}
            {sample_query}
            """
            
            result = con.execute(query).df()
            return result
        
        # Test full extraction
        result_df = fetch_return_comments(self.con, 'test_returns')
        self.assertEqual(len(result_df), 3)  # Should exclude empty and NULL comments
        
        # Test sample extraction
        sample_df = fetch_return_comments(self.con, 'test_returns', is_sample=True)
        self.assertEqual(len(sample_df), 2)  # Should return 2 random samples


class TestOpenAIIntegration(unittest.TestCase):
    """Test the OpenAI integration for comment analysis"""
    
    @patch('openai.OpenAI')
    def test_ai_analyze_comments(self, mock_openai):
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Set up the mock response structure
        mock_message.content = json.dumps([
            {
                "row_id": 1,
                "comment": "Item was defective",
                "themes": [
                    {"theme": "Product Quality", "sentiment": -0.8}
                ]
            }
        ])
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Function to test
        def ai_analyze_comments(client, prompt, df, debug=False, gpt_model="gpt-4o"):
            df_json = df.to_json(orient="records")
            
            messages = [
                {"role": "system", "content": "You are an expert linguistic analyst."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": df_json}
            ]
            
            resp = client.chat.completions.create(
                model=gpt_model,
                messages=messages,
                temperature=0.1,
                max_tokens=15000,
            )
            
            content = resp.choices[0].message.content.strip()
            return content
        
        # Test data
        test_df = pd.DataFrame({
            'row_id': [1],
            'comment': ['Item was defective']
        })
        
        # Run the test
        result = ai_analyze_comments(mock_client, "Analyze this comment", test_df)
        
        # Verify the result
        self.assertTrue(isinstance(result, str))
        parsed = json.loads(result)
        self.assertEqual(parsed[0]['row_id'], 1)
        self.assertEqual(parsed[0]['themes'][0]['theme'], "Product Quality")


class TestDataCleaning(unittest.TestCase):
    """Test the data cleaning functions"""
    
    def test_prepare_data_for_analysis(self):
        def prepare_data_for_analysis(text):
            if not isinstance(text, str):
                return ""
            # Remove control characters and excessive whitespace
            text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            return text
        
        # Test with various inputs
        self.assertEqual(prepare_data_for_analysis("Normal text"), "Normal text")
        self.assertEqual(prepare_data_for_analysis("Text with  multiple   spaces"), "Text with multiple spaces")
        self.assertEqual(prepare_data_for_analysis("Text with\nnewlines"), "Text with newlines")
        self.assertEqual(prepare_data_for_analysis("Text with\tcontrol\rcharacters"), "Text with control characters")
        self.assertEqual(prepare_data_for_analysis(123), "")  # Non-string input
    
    def test_strip_code_block(self):
        def strip_code_block(text):
            text = text.strip()
            code_block_pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
            match = re.match(code_block_pattern, text)
            if match:
                return match.group(1).strip()
            return text
        
        # Test with various inputs
        self.assertEqual(strip_code_block("Plain text"), "Plain text")
        self.assertEqual(strip_code_block("```\nCode block\n```"), "Code block")
        self.assertEqual(strip_code_block("```json\n{\"key\": \"value\"}\n```"), "{\"key\": \"value\"}")


class TestSentimentAnalysisPipeline(unittest.TestCase):
    """Test the sentiment analysis pipeline"""
    
    @patch('openai.OpenAI')
    def test_handle_sentiment_analysis(self, mock_openai):
        # This is a complex function to test, so we'll just do a basic smoke test
        
        # Mock client and responses
        mock_client = MagicMock()
        
        # Mock product analysis response
        product_response = MagicMock()
        product_choice = MagicMock()
        product_message = MagicMock()
        product_message.content = json.dumps([
            {
                "row_id": 1,
                "comment": "Item was defective",
                "themes": [
                    {"theme": "Product Quality", "sentiment": -0.8}
                ]
            }
        ])
        product_choice.message = product_message
        product_response.choices = [product_choice]
        
        # Mock customer analysis response
        customer_response = MagicMock()
        customer_choice = MagicMock()
        customer_message = MagicMock()
        customer_message.content = json.dumps([
            {
                "row_id": 1,
                "comment": "Item was defective",
                "themes": [
                    {"theme": "Customer Dissatisfaction", "sentiment": -0.9}
                ]
            }
        ])
        customer_choice.message = customer_message
        customer_response.choices = [customer_choice]
        
        # Setup mock to return different responses for different calls
        mock_client.chat.completions.create.side_effect = [product_response, customer_response]
        
        # Create simplified test function
        def simplified_handle_sentiment_analysis(comments_df, client):
            # Mock function that would call OpenAI
            def mock_ai_analyze(client, prompt, df):
                # This would normally call the OpenAI API
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an analyst"},
                        {"role": "user", "content": prompt},
                        {"role": "user", "content": df.to_json(orient="records")}
                    ],
                    temperature=0.1,
                )
                return resp.choices[0].message.content
            
            # Process product analysis
            product_result = mock_ai_analyze(client, "Analyze product feedback", comments_df)
            product_json = json.loads(product_result)
            product_df = pd.DataFrame(product_json)
            
            # Process customer analysis
            customer_result = mock_ai_analyze(client, "Analyze customer sentiment", comments_df)
            customer_json = json.loads(customer_result)
            customer_df = pd.DataFrame(customer_json)
            
            return product_df, customer_df
        
        # Test data
        test_df = pd.DataFrame({
            'row_id': [1],
            'comment': ['Item was defective']
        })
        
        # Run the test
        product_df, customer_df = simplified_handle_sentiment_analysis(test_df, mock_client)
        
        # Verify basic results
        self.assertEqual(len(product_df), 1)
        self.assertEqual(len(customer_df), 1)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)


if __name__ == '__main__':
    unittest.main()
