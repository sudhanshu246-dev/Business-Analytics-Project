import pandas as pd

class BusinessInsights:
    def __init__(self, df):
        self.df = df.copy()

    def generate_insights(self):
        insights = []
        try:
            if self.df.empty:
                return ['No data available to generate insights.']
            total_sales = self.df['SalesAmount'].sum() if 'SalesAmount' in self.df.columns else 0
            total_profit = self.df['Profit'].sum() if 'Profit' in self.df.columns else 0
            profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
            insights.append(f'Overall profit margin is {profit_margin:.2f}% across filtered data.')
            # Top category
            if 'Category' in self.df.columns and 'SalesAmount' in self.df.columns:
                cat = self.df.groupby('Category')['SalesAmount'].sum().sort_values(ascending=False)
                if not cat.empty:
                    insights.append(f'Top performing category by sales: {cat.index[0]} (${cat.iloc[0]:,.2f}).')
            # Region
            if 'Region' in self.df.columns and 'SalesAmount' in self.df.columns:
                reg = self.df.groupby('Region')['SalesAmount'].sum().sort_values(ascending=False)
                if not reg.empty:
                    insights.append(f'Best region by sales: {reg.index[0]} (${reg.iloc[0]:,.2f}).')
            # Top product
            if 'Product' in self.df.columns and 'SalesAmount' in self.df.columns:
                prod = self.df.groupby('Product')['SalesAmount'].sum().sort_values(ascending=False)
                if not prod.empty:
                    insights.append(f'Best-selling product: {prod.index[0]} (${prod.iloc[0]:,.2f}).')
            # Loss-making check
            if total_profit < 0:
                insights.append('Overall business is operating at a loss - review pricing/costs immediately.')
            elif profit_margin < 10:
                insights.append('Profit margin is low (<10%) - consider cost optimization or pricing review.')
            elif profit_margin < 20:
                insights.append('Profit margin is moderate (10-20%) - room for improvement through cost control.')
            else:
                insights.append('Business is profitable with healthy margins (>20%).')
            # Recommendations
            insights.append('Recommendation: Focus marketing on top category, region, and product to maximize revenue.')
            # Discount impact (data-driven)
            if {'Discount', 'SalesAmount', 'Profit'}.issubset(self.df.columns):
                d = self.df.groupby(self.df['Discount'] > 0)[['SalesAmount', 'Profit']].sum()
                if True in d.index and False in d.index and (d['SalesAmount'] > 0).all():
                    m = d['Profit'] / d['SalesAmount'] * 100
                    if m[True] < m[False]:
                        insights.append(f'Discounted orders earn a lower margin ({m[True]:.2f}%) than full-price orders ({m[False]:.2f}%) - review discount strategy.')
                    else:
                        insights.append(f'Discounted orders do not reduce margin ({m[True]:.2f}% vs {m[False]:.2f}% at full price) - current discounts look sustainable.')
            # Customer concentration (data-driven)
            if 'CustomerID' in self.df.columns and total_sales > 0:
                top_c = self.df.groupby('CustomerID')['SalesAmount'].sum().sort_values(ascending=False).head(10)
                insights.append(f'Top 10 customers contribute {top_c.sum() / total_sales * 100:.1f}% of sales - retain them with loyalty offers.')
            return insights
        except Exception as e:
            return [f'Error generating insights: {e}']
