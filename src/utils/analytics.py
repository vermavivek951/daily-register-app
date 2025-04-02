import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

class Analytics:
    def __init__(self, db_path):
        self.db_path = db_path
        self.reports_dir = os.path.join(os.path.dirname(db_path), 'reports')
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def get_daily_summary(self, date):
        """Get summary of transactions for a specific date"""
        conn = sqlite3.connect(self.db_path)
        query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(total_amount) as total_sales,
            SUM(cash_amount) as total_cash,
            SUM(card_amount) as total_card,
            SUM(upi_amount) as total_upi
        FROM transactions 
        WHERE date = '{date}'
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict('records')[0]

    def calculate_daily_profit(self, date):
        """Calculate profit for a specific date"""
        conn = sqlite3.connect(self.db_path)
        
        # Get all transactions for the date
        query = f"""
        SELECT * FROM transactions 
        WHERE date = '{date}'
        """
        df = pd.read_sql_query(query, conn)
        
        # Calculate total revenue
        total_revenue = df['total_amount'].sum()
        
        # You would need to implement your profit calculation logic here
        # For example: profit = revenue - costs
        # This is a placeholder calculation
        estimated_profit = total_revenue * 0.15  # 15% profit margin
        
        conn.close()
        return {
            'date': date,
            'total_revenue': total_revenue,
            'estimated_profit': estimated_profit
        }

    def generate_trends_report(self, start_date, end_date):
        """Generate trends report for a date range"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
        SELECT 
            date,
            COUNT(*) as transaction_count,
            SUM(total_amount) as daily_total,
            SUM(cash_amount) as cash_total,
            SUM(card_amount) as card_total,
            SUM(upi_amount) as upi_total
        FROM transactions 
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date
        ORDER BY date
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
            
        # Create visualizations
        plt.figure(figsize=(15, 10))
        
        # Daily totals
        plt.subplot(2, 2, 1)
        plt.plot(df['date'], df['daily_total'], marker='o')
        plt.title('Daily Total Sales')
        plt.xticks(rotation=45)
        
        # Payment method distribution
        plt.subplot(2, 2, 2)
        payment_methods = ['cash_total', 'card_total', 'upi_total']
        totals = [df[method].sum() for method in payment_methods]
        plt.pie(totals, labels=['Cash', 'Card', 'UPI'], autopct='%1.1f%%')
        plt.title('Payment Method Distribution')
        
        # Transaction count trend
        plt.subplot(2, 2, 3)
        plt.bar(df['date'], df['transaction_count'])
        plt.title('Daily Transaction Count')
        plt.xticks(rotation=45)
        
        # Save the plot
        plt.tight_layout()
        plot_path = os.path.join(self.reports_dir, f'trends_{start_date}_to_{end_date}.png')
        plt.savefig(plot_path)
        plt.close()
        
        return {
            'plot_path': plot_path,
            'summary_stats': {
                'total_sales': df['daily_total'].sum(),
                'avg_daily_sales': df['daily_total'].mean(),
                'total_transactions': df['transaction_count'].sum(),
                'avg_transaction_value': df['daily_total'].sum() / df['transaction_count'].sum(),
                'payment_distribution': {
                    'cash': df['cash_total'].sum(),
                    'card': df['card_total'].sum(),
                    'upi': df['upi_total'].sum()
                }
            }
        }

    def get_monthly_statistics(self, year, month):
        """Get monthly statistics"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
        SELECT *
        FROM transactions 
        WHERE strftime('%Y-%m', date) = '{year:04d}-{month:02d}'
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
            
        return {
            'total_sales': df['total_amount'].sum(),
            'total_transactions': len(df),
            'average_transaction': df['total_amount'].mean(),
            'busiest_day': df.groupby('date').size().idxmax(),
            'highest_sale_day': df.groupby('date')['total_amount'].sum().idxmax(),
            'payment_methods': {
                'cash': df['cash_amount'].sum(),
                'card': df['card_amount'].sum(),
                'upi': df['upi_amount'].sum()
            }
        } 