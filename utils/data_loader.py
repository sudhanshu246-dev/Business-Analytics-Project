import os
import pandas as pd

# Joins the normalized MySQL tables back into the flat layout used by the dashboard
DB_QUERY = """
SELECT o.order_id AS OrderID, o.order_date AS OrderDate,
       c.customer_id AS CustomerID, c.customer_name AS CustomerName,
       p.product_name AS Product, p.category AS Category, o.region AS Region,
       d.quantity AS Quantity, d.unit_price AS UnitPrice, d.discount AS Discount,
       d.sales_amount AS SalesAmount, d.profit AS Profit
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON d.product_id = p.product_id
"""


class DataLoader:
    def __init__(self, data_path=None):
        # Without an explicit path: try MySQL first, then fall back to CSV/Excel in data/
        self.use_db = data_path is None
        self.source_label = 'CSV file'
        self.db_note = ''
        if data_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Prefer sample_sales.csv, fallback to any csv/xlsx in data/
            sample_csv = os.path.join(base, 'data', 'sample_sales.csv')
            if os.path.exists(sample_csv):
                data_path = sample_csv
            else:
                data_dir = os.path.join(base, 'data')
                candidates = []
                if os.path.exists(data_dir):
                    for f in os.listdir(data_dir):
                        if f.lower().endswith(('.csv', '.xlsx', '.xls')):
                            candidates.append(os.path.join(data_dir, f))
                data_path = candidates[0] if candidates else sample_csv
        self.data_path = data_path

    def load_from_db(self):
        from config.db_config import get_db_config
        conn = get_db_config().get_connection()
        try:
            cur = conn.cursor()
            cur.execute(DB_QUERY)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            cur.close()
        finally:
            conn.close()
        if not rows:
            raise ValueError('MySQL tables are empty (run sql/load_data.sql)')
        return pd.DataFrame(rows, columns=cols)

    def load_data(self):
        if self.use_db:
            try:
                df = self.clean_data(self.load_from_db())
                if not df.empty:
                    self.source_label = 'MySQL database'
                    return df
            except Exception as e:
                self.db_note = str(e)
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f'Data file not found: {self.data_path}')
            ext = os.path.splitext(self.data_path)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(self.data_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(self.data_path)
            else:
                raise ValueError('Unsupported file format. Use CSV or Excel.')
            if df.empty:
                raise ValueError('Loaded dataset is empty.')
            df = self.clean_data(df)
            if df.empty:
                raise ValueError('Dataset is empty after cleaning. Check for missing/invalid data.')
            return df
        except Exception as e:
            raise Exception(f'Error loading data: {e}')

    def clean_data(self, df):
        try:
            df = df.copy()
            # Standardize column names if needed
            df.columns = [str(c).strip() for c in df.columns]
            # Convert dates
            if 'OrderDate' in df.columns:
                df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
            # Numeric conversions
            for col in ['Quantity', 'UnitPrice', 'Discount', 'SalesAmount', 'Profit']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            # Drop rows with critical missing values
            critical = []
            for c in ['OrderDate', 'SalesAmount', 'Profit']:
                if c in df.columns:
                    critical.append(c)
            if critical:
                df = df.dropna(subset=critical)
            # Fill remaining missing
            fill_map = {}
            for c in ['CustomerName', 'Product', 'Category', 'Region', 'CustomerID', 'OrderID']:
                if c in df.columns:
                    fill_map[c] = 'Unknown'
            if fill_map:
                df = df.fillna(fill_map)
            # Ensure non-negative where reasonable
            if 'Quantity' in df.columns:
                df = df[df['Quantity'] >= 0]
            if 'SalesAmount' in df.columns:
                df = df[df['SalesAmount'] >= 0]
            if 'Profit' in df.columns:
                df = df[df['Profit'].notna()]
            # One name per CustomerID: most frequent name (ties -> alphabetical), same rule as sql/load_data.sql
            if 'CustomerID' in df.columns and 'CustomerName' in df.columns and not df.empty:
                names = (df.groupby(['CustomerID', 'CustomerName']).size().reset_index(name='n')
                           .sort_values(['CustomerID', 'n', 'CustomerName'], ascending=[True, False, True])
                           .drop_duplicates('CustomerID').set_index('CustomerID')['CustomerName'])
                df['CustomerName'] = df['CustomerID'].map(names)
            return df
        except Exception as e:
            raise Exception(f'Error cleaning data: {e}')
