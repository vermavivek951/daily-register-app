import pandas as pd
from pathlib import Path
from typing import List
from ..models.transaction import Transaction

class ExcelExporter:
    @staticmethod
    def export_transactions(transactions: List[Transaction], date: str) -> str:
        # Create export directory if it doesn't exist
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        # Create filename
        filename = export_dir / f"jewelry_sales_{date}.xlsx"
        
        # Convert transactions to DataFrame
        data = []
        for transaction in transactions:
            values = [
                transaction.id,
                transaction.item_name,
                transaction.item_type,
                "Yes" if transaction.is_billable else "No",
                transaction.weight,
                transaction.total_amount,
                transaction.net_amount_paid,
                transaction.old_item_returned,
                transaction.old_item_weight,
                transaction.old_item_amount,
                transaction.payment_mode,
                transaction.comments
            ]
            data.append(values)
        
        # Create DataFrame
        columns = ["ID", "Item Name", "Type", "Billable", "Weight (gm)", 
                  "Total Amount", "Net Paid", "Old Item", "Old Item Weight", 
                  "Old Item Amount", "Payment", "Comments"]
        df = pd.DataFrame(data, columns=columns)
        
        # Calculate summary
        summary = {
            "Item Name": "TOTAL",
            "Weight (gm)": df[df["Type"] == "Gold"]["Weight (gm)"].sum(),
            "Total Amount": df["Total Amount"].sum(),
            "Net Paid": df["Net Paid"].sum(),
            "Old Item Weight": [
                df[df["Old Item"] == "Gold"]["Old Item Weight"].sum(),
                df[df["Old Item"] == "Silver"]["Old Item Weight"].sum()
            ],
            "Old Item Amount": df["Old Item Amount"].sum()
        }
        
        # Add silver weight in comments
        summary["Comments"] = f"Silver Weight: {df[df['Type'] == 'Silver']['Weight (gm)'].sum()} gm"
        
        # Export to Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Sales", index=False)
            
            # Get the workbook and sheet
            workbook = writer.book
            sheet = writer.sheets["Sales"]
            
            # Add summary row
            sheet.append([])
            sheet.append(["SUMMARY", "", "", "", 
                        f"Gold: {summary['Weight (gm)']} gm", 
                        summary["Total Amount"],
                        summary["Net Paid"],
                        "",
                        f"Old Gold: {summary['Old Item Weight'][0]} gm, Old Silver: {summary['Old Item Weight'][1]} gm",
                        summary["Old Item Amount"],
                        "", summary["Comments"]])
            
            # Format currency columns
            for row in range(2, sheet.max_row):  # Skip header
                for col in [6, 7, 10]:  # Total Amount, Net Paid, and Old Item Amount columns
                    cell = sheet.cell(row=row, column=col)
                    cell.number_format = "₹#,##0.00"
        
        return str(filename) 