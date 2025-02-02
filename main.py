#!/usr/bin/env python3
"""
Small Business Invoicing & Accounting Software (Modern Premium UI with Enhanced Dashboard & Tables)
Author: Your Name
Date: 2025-02-02
Description:
  A full-screen desktop application built with PyQt5 that allows small businesses,
  freelancers, and startups to manage invoices, expenses, view reports, and see a dashboard.
  All data is stored in computer memory.
  
  Features include:
    - Full-screen launch
    - Custom icons, toolbar, and menu for enhanced usability
    - Search/filter, editing, deletion, and CSV export
    - An enhanced Dashboard with two Matplotlib charts: a bar chart and a pie chart
    - Improved table styling in all tabs for a cleaner, more modern look
"""

import sys
import csv
import warnings
from datetime import datetime

# Suppress sip deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# PyQt5 imports
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QDialog, QFormLayout, QDateEdit, QMessageBox, QComboBox,
    QFileDialog, QToolBar, QAction, QStatusBar, QDoubleSpinBox
)

# Matplotlib imports for Dashboard
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ---------------------------------
# Data Models (stored in memory)
# ---------------------------------
class Invoice:
    _id_counter = 1

    def __init__(self, customer, invoice_date, due_date, amount):
        self.id = Invoice._id_counter
        Invoice._id_counter += 1
        self.customer = customer
        self.invoice_date = invoice_date
        self.due_date = due_date
        self.amount = amount
        self.status = "Unpaid"  # or "Paid"

    def mark_paid(self):
        self.status = "Paid"


class Expense:
    _id_counter = 1

    def __init__(self, category, description, date, amount):
        self.id = Expense._id_counter
        Expense._id_counter += 1
        self.category = category
        self.description = description
        self.date = date
        self.amount = amount

# ---------------------------------
# Dialogs for Adding / Editing Data
# ---------------------------------
class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        """
        If invoice is provided, the dialog works in edit mode.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Invoice" if invoice else "Add Invoice")
        self.setModal(True)
        self.invoice = invoice  # if editing, an Invoice object
        self.parent_window = parent  # Store parent window reference
        self.setup_ui()
        if self.invoice:
            self.prefill_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Customer Input
        customer_layout = QHBoxLayout()
        customer_label = QLabel("Customer Name:")
        customer_label.setStyleSheet("font-weight: bold;")
        self.customer_input = QLineEdit()
        self.customer_input.setMinimumWidth(300)
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_input)
        layout.addLayout(customer_layout)

        # Invoice Date Input
        date_layout = QHBoxLayout()
        invoice_date_label = QLabel("Invoice Date:")
        invoice_date_label.setStyleSheet("font-weight: bold;")
        self.invoice_date = QDateEdit(calendarPopup=True)
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setMinimumWidth(300)
        date_layout.addWidget(invoice_date_label)
        date_layout.addWidget(self.invoice_date)
        layout.addLayout(date_layout)

        # Due Date Input
        due_date_layout = QHBoxLayout()
        due_date_label = QLabel("Due Date:")
        due_date_label.setStyleSheet("font-weight: bold;")
        self.due_date = QDateEdit(calendarPopup=True)
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setMinimumWidth(300)
        due_date_layout.addWidget(due_date_label)
        due_date_layout.addWidget(self.due_date)
        layout.addLayout(due_date_layout)

        # Amount Input
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet("font-weight: bold;")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimumWidth(300)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Update" if self.invoice else "Add Invoice")
        self.btn_cancel = QPushButton("Cancel")
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.resize(500, 350)  # Increased dialog size
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove ? button
        
        # Connect buttons
        self.btn_save.clicked.connect(self.accept_data)
        self.btn_cancel.clicked.connect(self.reject)

    def prefill_data(self):
        """Fill in the fields with the current invoice data for editing."""
        self.customer_input.setText(self.invoice.customer)
        self.invoice_date.setDate(QDate(self.invoice.invoice_date.year,
                                             self.invoice.invoice_date.month,
                                             self.invoice.invoice_date.day))
        self.due_date.setDate(QDate(self.invoice.due_date.year,
                                         self.invoice.due_date.month,
                                         self.invoice.due_date.day))
        self.amount_input.setValue(self.invoice.amount)

    def accept_data(self):
        try:
            customer = self.customer_input.text().strip()
            if not customer:
                raise ValueError("Customer name is required.")
            
            invoice_date = self.invoice_date.date().toPyDate()
            due_date = self.due_date.date().toPyDate()
            amount = self.amount_input.value()

            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            if self.invoice:  # Edit mode: update the existing invoice.
                self.invoice.customer = customer
                self.invoice.invoice_date = invoice_date
                self.invoice.due_date = due_date
                self.invoice.amount = amount
                QMessageBox.information(self, "Success", "Invoice updated successfully.")
            else:  # Add mode: create a new invoice
                # Create the invoice and store it so it can be accessed by the parent
                self.invoice = Invoice(customer, invoice_date, due_date, amount)
                QMessageBox.information(self, "Success", "Invoice added successfully.")
            
            self.accept()  # Close the dialog
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {str(e)}")


class ExpenseDialog(QDialog):
    def __init__(self, parent=None, expense=None):
        """
        If expense is provided, the dialog works in edit mode.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Expense" if expense else "Add Expense")
        self.setModal(True)
        self.expense = expense
        self.parent_window = parent  # Store parent window reference
        self.setup_ui()
        if self.expense:
            self.prefill_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Category Input
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        category_label.setStyleSheet("font-weight: bold;")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Office Supplies", "Travel", "Utilities", "Software", "Other"])
        self.category_combo.setMinimumWidth(300)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        # Description Input
        description_layout = QHBoxLayout()
        description_label = QLabel("Description:")
        description_label.setStyleSheet("font-weight: bold;")
        self.description_input = QLineEdit()
        self.description_input.setMinimumWidth(300)
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_input)
        layout.addLayout(description_layout)

        # Date Input
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setStyleSheet("font-weight: bold;")
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumWidth(300)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Amount Input
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet("font-weight: bold;")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimumWidth(300)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Update" if self.expense else "Add Expense")
        self.btn_cancel = QPushButton("Cancel")
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.resize(500, 350)  # Increased dialog size
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove ? button
        
        # Connect buttons
        self.btn_save.clicked.connect(self.accept_data)
        self.btn_cancel.clicked.connect(self.reject)

    def prefill_data(self):
        self.category_combo.setCurrentText(self.expense.category)
        self.description_input.setText(self.expense.description)
        self.date_input.setDate(QDate(self.expense.date.year,
                                     self.expense.date.month,
                                     self.expense.date.day))
        self.amount_input.setValue(self.expense.amount)

    def accept_data(self):
        try:
            category = self.category_combo.currentText()
            description = self.description_input.text().strip()
            if not description:
                raise ValueError("Description is required.")
            
            date = self.date_input.date().toPyDate()
            amount = self.amount_input.value()

            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            if self.expense:
                self.expense.category = category
                self.expense.description = description
                self.expense.date = date
                self.expense.amount = amount
                QMessageBox.information(self, "Success", "Expense updated successfully.")
            else:
                # Create the expense and store it so it can be accessed by the parent
                self.expense = Expense(category, description, date, amount)
                QMessageBox.information(self, "Success", "Expense added successfully.")
            
            self.accept()  # Close the dialog
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {str(e)}")

# ---------------------------------
# Enhanced Dashboard Tab (with Two Charts)
# ---------------------------------
class DashboardTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # for accessing invoices and expenses
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        # Create a Figure with two subplots: one for bar chart, one for pie chart.
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot_charts()

    def plot_charts(self):
        # Clear the figure
        self.figure.clear()
        
        # Set figure background color
        self.figure.patch.set_facecolor('#2c2c2c')
        
        # Create subplots: bar chart on left, pie chart on right
        ax_bar = self.figure.add_subplot(1, 2, 1)
        ax_pie = self.figure.add_subplot(1, 2, 2)
        
        # Set axes background colors
        ax_bar.set_facecolor('#353535')
        ax_pie.set_facecolor('#353535')
        
        # Data calculations
        total_invoiced = sum(inv.amount for inv in self.parent.invoices)
        total_paid = sum(inv.amount for inv in self.parent.invoices if inv.status == "Paid")
        total_expenses = sum(exp.amount for exp in self.parent.expenses)
        net_profit = total_paid - total_expenses

        # Bar Chart Data
        categories = ['Total Invoiced', 'Total Paid', 'Total Expenses', 'Net Profit']
        values = [total_invoiced, total_paid, total_expenses, net_profit]
        bar_colors = ['#4a90e2', '#50e3c2', '#f5a623', '#7ed321']

        # Pie Chart Data (Paid vs Unpaid Invoices)
        paid_count = sum(1 for inv in self.parent.invoices if inv.status == "Paid")
        unpaid_count = sum(1 for inv in self.parent.invoices if inv.status != "Paid")
        pie_labels = ['Paid', 'Unpaid'] if (paid_count + unpaid_count) > 0 else []
        pie_values = [paid_count, unpaid_count] if (paid_count + unpaid_count) > 0 else [0, 0]
        pie_colors = ['#50e3c2', '#f5a623']

        # Bar Chart
        bars = ax_bar.bar(categories, values, color=bar_colors, edgecolor='white')
        ax_bar.set_title("Financial Summary", fontsize=14, color="#dcdcdc")
        ax_bar.tick_params(axis='x', colors="#dcdcdc", labelsize=10)
        ax_bar.tick_params(axis='y', colors="#dcdcdc")
        for spine in ax_bar.spines.values():
            spine.set_color('#555555')
        ax_bar.grid(True, linestyle='--', alpha=0.5, color='#555555')

        # Annotate each bar with its value
        for bar in bars:
            height = bar.get_height()
            ax_bar.annotate(f'{height:.2f}', 
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            color="#dcdcdc", fontsize=10)

        # Pie Chart Styling
        if sum(pie_values) > 0:
            wedges, texts, autotexts = ax_pie.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', startangle=90, colors=pie_colors,
                                                  textprops={'color': "#dcdcdc", 'fontsize': 10})
            ax_pie.set_title("Invoice Status", fontsize=14, color="#dcdcdc")
            for text in texts:
                text.set_color("#dcdcdc")
        else:
            ax_pie.text(0.5, 0.5, "No Invoice Data", horizontalalignment='center',
                        verticalalignment='center', color="#dcdcdc", fontsize=12)
            ax_pie.axis('off')

        # Adjust subplot spacing
        self.figure.subplots_adjust(wspace=0.3)

        self.canvas.draw()

    def refresh(self):
        self.plot_charts()

# ---------------------------------
# Main Application Tabs with Improved Table Styling
# ---------------------------------
class InvoicesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # reference to main window for accessing invoice list
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Search Field
        search_layout = QHBoxLayout()
        search_label = QLabel("Search by Customer:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        # Table for invoices
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Customer", "Invoice Date", "Due Date", "Amount", "Status"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        
        # Improved table styling
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #353535;
                color: #dcdcdc;
                padding: 5px;
                border: 1px solid #2c2c2c;
                font-weight: bold;
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2c2c2c;
                alternate-background-color: #353535;
                color: #dcdcdc;
                selection-background-color: #4a90e2;
            }
        """)
        
        # Enable alternating row colors
        self.table.setAlternatingRowColors(True)
        
        # Adjust column widths
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 200)  # Customer
        self.table.setColumnWidth(2, 150)  # Invoice Date
        self.table.setColumnWidth(3, 150)  # Due Date
        self.table.setColumnWidth(4, 100)  # Amount
        self.table.setColumnWidth(5, 100)  # Status
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(400)  # Increased table height
        main_layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self.btn_add_invoice = QPushButton("Add Invoice")
        self.btn_edit_invoice = QPushButton("Edit Invoice")
        self.btn_delete_invoice = QPushButton("Delete Invoice")
        self.btn_mark_paid = QPushButton("Mark as Paid")
        btn_layout.addWidget(self.btn_add_invoice)
        btn_layout.addWidget(self.btn_edit_invoice)
        btn_layout.addWidget(self.btn_delete_invoice)
        btn_layout.addWidget(self.btn_mark_paid)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Signals
        self.btn_add_invoice.clicked.connect(self.open_add_invoice_dialog)
        self.btn_edit_invoice.clicked.connect(self.edit_invoice)
        self.btn_delete_invoice.clicked.connect(self.delete_invoice)
        self.btn_mark_paid.clicked.connect(self.mark_invoice_paid)
        self.search_edit.textChanged.connect(self.refresh_table)
        self.table.doubleClicked.connect(self.edit_invoice)

    def open_add_invoice_dialog(self):
        dialog = InvoiceDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.invoice:
            self.parent.invoices.append(dialog.invoice)
            self.refresh_table()
            self.parent.dashboard_tab.refresh()

    def edit_invoice(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select an invoice to edit.")
            return
        row = selected_rows[0].row()
        invoice_id = int(self.table.item(row, 0).text())
        invoice = next((inv for inv in self.parent.invoices if inv.id == invoice_id), None)
        if invoice:
            dialog = InvoiceDialog(self, invoice)
            dialog.exec_()
            self.refresh_table()
            self.parent.dashboard_tab.refresh()

    def delete_invoice(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select an invoice to delete.")
            return
        reply = QMessageBox.question(self, "Delete Invoice",
                                     "Are you sure you want to delete the selected invoice?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for index in selected_rows:
                row = index.row()
                invoice_id = int(self.table.item(row, 0).text())
                self.parent.invoices = [inv for inv in self.parent.invoices if inv.id != invoice_id]
            self.refresh_table()
            self.parent.dashboard_tab.refresh()

    def mark_invoice_paid(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select an invoice to mark as paid.")
            return
        for index in selected_rows:
            row = index.row()
            invoice_id = int(self.table.item(row, 0).text())
            for invoice in self.parent.invoices:
                if invoice.id == invoice_id:
                    invoice.mark_paid()
                    break
        self.refresh_table()
        self.parent.dashboard_tab.refresh()

    def refresh_table(self):
        filter_text = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        for invoice in self.parent.invoices:
            if filter_text and filter_text not in invoice.customer.lower():
                continue
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(str(invoice.id)))
            self.table.setItem(row_pos, 1, QTableWidgetItem(invoice.customer))
            self.table.setItem(row_pos, 2, QTableWidgetItem(invoice.invoice_date.strftime("%Y-%m-%d")))
            self.table.setItem(row_pos, 3, QTableWidgetItem(invoice.due_date.strftime("%Y-%m-%d")))
            self.table.setItem(row_pos, 4, QTableWidgetItem(f"{invoice.amount:.2f}"))
            self.table.setItem(row_pos, 5, QTableWidgetItem(invoice.status))
        self.table.resizeColumnsToContents()


class ExpensesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Search Field
        search_layout = QHBoxLayout()
        search_label = QLabel("Search by Description:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        # Table for expenses
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Category", "Description", "Date", "Amount"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        
        # Improved table styling
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #353535;
                color: #dcdcdc;
                padding: 5px;
                border: 1px solid #2c2c2c;
                font-weight: bold;
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2c2c2c;
                alternate-background-color: #353535;
                color: #dcdcdc;
                selection-background-color: #4a90e2;
            }
        """)
        
        # Enable alternating row colors
        self.table.setAlternatingRowColors(True)
        
        # Adjust column widths
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 150)  # Category
        self.table.setColumnWidth(2, 250)  # Description
        self.table.setColumnWidth(3, 150)  # Date
        self.table.setColumnWidth(4, 100)  # Amount
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(400)  # Increased table height
        main_layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self.btn_add_expense = QPushButton("Add Expense")
        self.btn_edit_expense = QPushButton("Edit Expense")
        self.btn_delete_expense = QPushButton("Delete Expense")
        btn_layout.addWidget(self.btn_add_expense)
        btn_layout.addWidget(self.btn_edit_expense)
        btn_layout.addWidget(self.btn_delete_expense)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Signals
        self.btn_add_expense.clicked.connect(self.open_add_expense_dialog)
        self.btn_edit_expense.clicked.connect(self.edit_expense)
        self.btn_delete_expense.clicked.connect(self.delete_expense)
        self.search_edit.textChanged.connect(self.refresh_table)
        self.table.doubleClicked.connect(self.edit_expense)

    def open_add_expense_dialog(self):
        dialog = ExpenseDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.expense:
            self.parent.expenses.append(dialog.expense)
            self.refresh_table()
            self.parent.dashboard_tab.refresh()

    def edit_expense(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select an expense to edit.")
            return
        row = selected_rows[0].row()
        expense_id = int(self.table.item(row, 0).text())
        expense = next((exp for exp in self.parent.expenses if exp.id == expense_id), None)
        if expense:
            dialog = ExpenseDialog(self, expense)
            dialog.exec_()
            self.refresh_table()
            self.parent.dashboard_tab.refresh()

    def delete_expense(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select an expense to delete.")
            return
        reply = QMessageBox.question(self, "Delete Expense",
                                     "Are you sure you want to delete the selected expense?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for index in selected_rows:
                row = index.row()
                expense_id = int(self.table.item(row, 0).text())
                self.parent.expenses = [exp for exp in self.parent.expenses if exp.id != expense_id]
            self.refresh_table()
            self.parent.dashboard_tab.refresh()

    def refresh_table(self):
        filter_text = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        for expense in self.parent.expenses:
            if filter_text and filter_text not in expense.description.lower():
                continue
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(str(expense.id)))
            self.table.setItem(row_pos, 1, QTableWidgetItem(expense.category))
            self.table.setItem(row_pos, 2, QTableWidgetItem(expense.description))
            self.table.setItem(row_pos, 3, QTableWidgetItem(expense.date.strftime("%Y-%m-%d")))
            self.table.setItem(row_pos, 4, QTableWidgetItem(f"{expense.amount:.2f}"))
        self.table.resizeColumnsToContents()


class ReportsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.label_report = QLabel()
        self.label_report.setAlignment(Qt.AlignTop)
        self.label_report.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_report.setMinimumHeight(250)
        main_layout.addWidget(self.label_report)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self.btn_refresh = QPushButton("Refresh Report")
        self.btn_export = QPushButton("Export CSV")
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        self.btn_refresh.clicked.connect(self.generate_report)
        self.btn_export.clicked.connect(self.export_csv)
        self.generate_report()

    def generate_report(self):
        total_invoiced = sum(inv.amount for inv in self.parent.invoices)
        total_paid = sum(inv.amount for inv in self.parent.invoices if inv.status == "Paid")
        total_expenses = sum(exp.amount for exp in self.parent.expenses)
        net_profit = total_paid - total_expenses
        tax_rate = 0.10
        tax_due = net_profit * tax_rate if net_profit > 0 else 0

        report_text = (
            "<h2 style='color:#F1C40F;'>Financial Report</h2>"
            f"<p><b>Total Invoiced:</b> ${total_invoiced:.2f}</p>"
            f"<p><b>Total Paid:</b> ${total_paid:.2f}</p>"
            f"<p><b>Total Expenses:</b> ${total_expenses:.2f}</p>"
            f"<p><b>Net Profit:</b> ${net_profit:.2f}</p>"
            f"<p><b>Estimated Tax (10%):</b> ${tax_due:.2f}</p>"
        )
        self.label_report.setText(report_text)

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    # Write Invoices section
                    writer.writerow(["Invoices"])
                    writer.writerow(["ID", "Customer", "Invoice Date", "Due Date", "Amount", "Status"])
                    for inv in self.parent.invoices:
                        writer.writerow([inv.id, inv.customer,
                                         inv.invoice_date.strftime("%Y-%m-%d"),
                                         inv.due_date.strftime("%Y-%m-%d"),
                                         f"{inv.amount:.2f}", inv.status])
                    writer.writerow([])  # Blank row
                    # Write Expenses section
                    writer.writerow(["Expenses"])
                    writer.writerow(["ID", "Category", "Description", "Date", "Amount"])
                    for exp in self.parent.expenses:
                        writer.writerow([exp.id, exp.category, exp.description,
                                         exp.date.strftime("%Y-%m-%d"), f"{exp.amount:.2f}"])
                QMessageBox.information(self, "Export CSV", "Data exported successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Export CSV", f"An error occurred: {str(e)}")

# ---------------------------------
# Main Window with Menu/Toolbar
# ---------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoicing & Accounting")
        self.resize(950, 700)
        
        # In-memory storage for invoices and expenses
        self.invoices = []
        self.expenses = []

        self.setup_ui()
        self.create_menu_toolbar()
        self.statusBar().showMessage("Welcome to Invoicing & Accounting App")

    def setup_ui(self):
        self.tabs = QTabWidget()

        # Create tabs with icons (ensure icon paths exist)
        self.dashboard_tab = DashboardTab(self)
        self.invoices_tab = InvoicesTab(self)
        self.expenses_tab = ExpensesTab(self)
        self.reports_tab = ReportsTab(self)

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.invoices_tab, "Invoices")
        self.tabs.addTab(self.expenses_tab, "Expenses")
        self.tabs.addTab(self.reports_tab, "Reports")

        self.setCentralWidget(self.tabs)

    def create_menu_toolbar(self):
        # Create a toolbar with common actions
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Action: New Invoice
        action_new_invoice = QAction("New Invoice", self)
        action_new_invoice.triggered.connect(lambda: self.invoices_tab.open_add_invoice_dialog())
        toolbar.addAction(action_new_invoice)

        # Action: New Expense
        action_new_expense = QAction("New Expense", self)
        action_new_expense.triggered.connect(lambda: self.expenses_tab.open_add_expense_dialog())
        toolbar.addAction(action_new_expense)

        # Action: Refresh Dashboard
        action_refresh = QAction("Refresh Dashboard", self)
        action_refresh.triggered.connect(lambda: self.dashboard_tab.refresh())
        toolbar.addAction(action_refresh)

        # Create a menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(action_new_invoice)
        file_menu.addAction(action_new_expense)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def refresh_all(self):
        self.invoices_tab.refresh_table()
        self.expenses_tab.refresh_table()
        self.reports_tab.generate_report()
        self.dashboard_tab.refresh()

# ---------------------------------
# Main Function
# ---------------------------------
def main():
    app = QApplication(sys.argv)
    
    # Apply a premium dark-themed stylesheet with refined colors
    style = """
    /* Main Window */
    QMainWindow {
        background-color: #1e1e2f;
    }

    /* General Widgets */
    QWidget {
        font-family: "Segoe UI", sans-serif;
        font-size: 15px;
        color: #dcdcdc;
        background-color: #1e1e2f;
    }
    QLabel {
        color: #dcdcdc;
    }

    /* QPushButton */
    QPushButton {
        background-color: #3a3f58;
        border: 1px solid #4a90e2;
        border-radius: 5px;
        padding: 8px 16px;
        color: #ffffff;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #4a90e2;
    }
    QPushButton:pressed {
        background-color: #357ABD;
    }

    /* QLineEdit, QDateEdit, QComboBox */
    QLineEdit, QDateEdit, QComboBox {
        background-color: #2b2b3d;
        color: #dcdcdc;
        border: 1px solid #4a4a6a;
        border-radius: 4px;
        padding: 6px;
    }

    /* QTableWidget */
    QTableWidget {
        background-color: #2b2b3d;
        color: #dcdcdc;
        gridline-color: #3a3f58;
        border: none;
    }
    QTableWidget::item {
        padding: 4px;
    }
    QTableWidget QHeaderView::section {
        background-color: #3a3f58;
        color: #ffffff;
        padding: 8px;
        border: none;
    }

    /* QTabWidget */
    QTabWidget::pane {
        border: none;
    }
    QTabBar::tab {
        background: #2b2b3d;
        border: 1px solid #4a4a6a;
        padding: 10px 20px;
        margin: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 120px;
    }
    QTabBar::tab:selected {
        background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #357ABD);
        border-bottom: 2px solid #4a90e2;
    }
    QTabBar::tab:hover {
        background: #4a90e2;
    }

    /* QMessageBox */
    QMessageBox {
        background-color: #1e1e2f;
        color: #dcdcdc;
    }

    /* QDialog */
    QDialog {
        background-color: #2b2b3d;
    }
    QDialog QLineEdit, QDialog QDateEdit, QDialog QComboBox {
        background-color: #3a3f58;
    }
    QDialog QPushButton {
        background-color: #357ABD;
    }
    QDialog QPushButton:hover {
        background-color: #4a90e2;
    }
    """
    app.setStyleSheet(style)

    window = MainWindow()
    window.showMaximized()  # Launch in full-screen (maximized)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
