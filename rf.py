# Shamelessly copied from http://flask.pocoo.org/docs/quickstart/

from flask import request, Flask, render_template
from flaskext.mysql import MySQL

app = Flask(__name__, template_folder='./templates')
mysql = MySQL()
mysql.init_app(app)

db_con = MySQL(app, prefix="my_database", host="localhost", user="root", password="123", db="bank", autocommit=True)


@app.route('/')
def hello_world():
    data = ()
    cursor = db_con.get_db().cursor()
    cursor.execute("select * from Bank", data)
    rows = cursor.fetchall()
    res_data = {"a": 11, "b": {"c": 44}, "bank_rows": rows}
    return render_template('index.html', sam_context=res_data)


@app.route('/reports')
def get_reports():
    context = {}
    try:
        data = ()
        cursor = db_con.get_db().cursor()
        questions = {
            "a": {
                "q": "Show the full name of the customers who hold an account In Bank 'AL-Habib'",
                "proof": {
                    "name": "Connection of all customer-bank-branch-accounts",
                    "sql": """
                            select c.CustomerId as Id, FName, c.City, b.BankName, bb.BranchId, OpeningBalance as Obalance,
                            sa.SavingAccountNo as AccId, 'Saving' as AccType
                            from Customer c
                            join CustomerSavingAccount csa on csa.CustomerId=c.CustomerId
                            join SavingAccount sa on sa.SavingAccountNo=csa.AccountNo
                            join BankBranch bb on bb.BranchId=sa.BranchId
                            join Bank b on b.BankId=bb.BankId
                            UNION
                            select c.CustomerId as Id, FName, c.City, b.BankName, bb.BranchId, OpeningBalance as Obalance,
                            la.LoanAccountNo as AccId, 'Loan' as AccType
                            from Customer c
                            join CustomerLoanAccount cla on cla.CustomerId=c.CustomerId
                            join LoanAccount la on la.LoanAccountNo=cla.AccountNo
                            join BankBranch bb on bb.BranchId=la.BranchId
                            join Bank b on b.BankId=bb.BankId;
                        """
                },
                "ans": """
                        select concat(FName,' ',LName) as FullName, bb.BranchId from Customer c
                        join CustomerSavingAccount csa on csa.CustomerId=c.CustomerId
                        join SavingAccount sa on sa.SavingAccountNo=csa.AccountNo
                        join BankBranch bb on bb.BranchId=sa.BranchId
                        join Bank b on b.BankId=bb.BankId
                        WHERE b.BankName='Al-Habib'
                        UNION
                        select concat(FName,' ',LName) as FullName, bb.BranchId from Customer c
                        join CustomerLoanAccount cla on cla.CustomerId=c.CustomerId
                        join LoanAccount la on la.LoanAccountNo=cla.AccountNo
                        join BankBranch bb on bb.BranchId=la.BranchId
                        join Bank b on b.BankId=bb.BankId
                        WHERE b.BankName='Al-Habib';
                    """
            },
            "b": {
                "q": """Show the total saving transactions made In each bank.
                         (Show the bank name and the no. of transactions)""",
                "ans": """
                        select BankName, count(*) as NumerOfSavingTransactions from Bank b
                        join BankBranch bb on bb.BankId=b.BankId
                        join SavingAccount sa on sa.BranchId=bb.BranchId
                        join SavingTransaction st on st.SavingAccountNo=sa.SavingAccountNo
                        GROUP by b.BankName;
                        """
            },
            "c": {
                "q": "Show the names of the customers who opened the a saving account with maximum opening balance.",
                "proof": {
                    "name": "Opening Balance Of All SavingAccounts",
                    "sql": """
                            select Fname, Lname, sa.OpeningBalance from Customer c
                            join CustomerSavingAccount csa on csa.CustomerId=c.CustomerId
                            join SavingAccount sa on sa.SavingAccountNo=csa.AccountNo
                            ORDER by sa.OpeningBalance DESC;
                        """
                },
                "ans": """
                        select Fname, Lname, sa.OpeningBalance from Customer c
                        join CustomerSavingAccount csa on csa.CustomerId=c.CustomerId
                        join SavingAccount sa on sa.SavingAccountNo=csa.AccountNo
                        ORDER by sa.OpeningBalance DESC limit 1;
                    """
            },
            "d": {
                "q": """
                    How many loan accounts have more than I customers associated with it.
                    """,
                "proof": {
                    "name": "All Customers and their LoanAccounts",
                    "sql": """
                        SELECT count(*), group_concat(la.LoanAccountNo) as Accounts, cla.CustomerId from LoanAccount la
                        join CustomerLoanAccount cla on cla.AccountNo=la.LoanAccountNo
                        join Customer c on c.CustomerId=cla.CustomerId
                        GROUP by cla.CustomerId
                        """
                },
                "ans": """
                        SELECT count(*) CustomerCountWithMultipleLoanAccount from
                        (
                            SELECT count(*),cla.CustomerId from LoanAccount la
                            join CustomerLoanAccount cla on cla.AccountNo=la.LoanAccountNo
                            GROUP by cla.CustomerId
                            having count(*) > 1
                        ) tbl;
                    """
                
            },
            "e": {
                "q": """
                        Show the transactions of all saving accounts of MCB Bank.
                        (You should display account details even if no transactions have been made for the said account ).
                    """,
                "ans": """
                        SELECT sa.*, st.* from Bank b
                        inner join BankBranch bb on bb.BankId=b.BankId
                        inner join SavingAccount sa on sa.BranchId=bb.BranchId
                        left outer join SavingTransaction st on st.SavingAccountNo=sa.SavingAccountNo;
                    """
            },
            "f": {
                "q": "Show the name of customers from Islamabad who do not have a loan account.",
                "ans": """
                        SELECT distinct c.FName,c.LName from Customer c
                        left join CustomerLoanAccount cla on cla.CustomerId=c.CustomerId
                        where c.City='Islamabad' and cla.CustomerId is null;
                    """
            },
            "g": {
                "q": "Show the accounts opened in 2021 by customers living in Karachi.",
                "proof": {
                    "name": "Simple Answer taking only loan Accounts",
                    "sql": """
                        SELECT la.* FROM `Customer` c
                        join CustomerLoanAccount cla on cla.CustomerId=c.CustomerId
                        join LoanAccount la on la.LoanAccountNo=cla.AccountNo
                        where c.City='Karachi' and year(la.OpeningDate)=2021;
                        """
                },
                "ans": """
                        SELECT 'Loan Account' as Tablename, la.LoanAccountNo as AccNo, la.OpeningDate FROM `Customer` c
                        join CustomerLoanAccount cla on cla.CustomerId=c.CustomerId
                        join LoanAccount la on la.LoanAccountNo=cla.AccountNo
                        where c.City='Karachi' and year(la.OpeningDate)=2021

                        Union

                        SELECT 'Saving Account' as Tablename, sa.SavingAccountNo as AccNo, sa.OpeningDate FROM `Customer` c
                        join CustomerSavingAccount csa on csa.CustomerId=c.CustomerId
                        join SavingAccount sa on sa.SavingAccountNo=csa.AccountNo
                        where c.City='Karachi' and year(sa.OpeningDate)=2021;
                    """
            },
            "h": {
                "q": """
                    Show the names of the customers from Lahore who have a loan account and opening balance
                     less than 10K. (Use Nested Query)
                    """,
                "proof": {
                    "name": "Full Records for clarity",
                    "sql": """
                        select c.FName,c.LName, la.OpeningBalance, c.City from Customer c
                        join CustomerLoanAccount cla on cla.CustomerId=c.CustomerId
                        join LoanAccount la on la.LoanAccountNo=cla.AccountNo;
                        """
                },
                "ans": """
                        select FName, LName from Customer
                        where City='Lahore' and CustomerId in
                        (
                            select CustomerId from CustomerLoanAccount WHERE AccountNo IN
                            (SELECT LoanAccountNo from LoanAccount where OpeningBalance<10000)
                        );
                    """
            },
            "i": {
                "q": "Show the names and address of customers who have a loan account. (Use EXISTS)",
                "proof": {
                    "name": "Proof by showing All Customers",
                    "sql": """
                        SELECT FName,LName from Customer;
                        """
                },
                "ans": """
                        SELECT FName,LName from Customer
                        WHERE EXISTS (
                            SELECT * FROM CustomerLoanAccount
                            WHERE Customer.CustomerId = CustomerLoanAccount.CustomerId
                        );
                    """
            },
        }
        table_names = [
            "Bank",
            "BankBranch",
            "LoanAccount",
            "SavingAccount",
            "LoanAccount",
            "SavingAccount",
            "LoanTransaction",
            "SavingTransaction",
            "CustomerLoanAccount",
            "CustomerSavingAccount",
            "Customer",
        ]
        answers = []
        for opt in questions:
            item = questions[opt]
            if item.get("proof"):
                sql = item['proof']['sql']
                cursor.execute(sql)
                rows = cursor.fetchall()
                item['proof']['columns'] = [x[0] for x in cursor.description]
                item['proof']['data'] = rows
            sql = item['ans']
            item['sql'] = sql
            cursor.execute(sql)
            rows = cursor.fetchall()
            item['columns'] = [x[0] for x in cursor.description]
            item['data'] = rows
            item['serial'] = opt
            answers.append(item)
        tables_data = []
        for tbl in table_names:
            sql = "select * from "+tbl
            cursor.execute(sql)
            rows = cursor.fetchall()
            item = {"name": tbl, 'columns': [x[0] for x in cursor.description], 'data': rows}
            tables_data.append(item)
        context = {'answers': answers, 'tables': tables_data}
    except Exception as ex:
        mes = str(ex)
        a = 1
    
    return render_template('reports.html', context=context)


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        first_name = request.form.get('first_name') or 'No Fname'
        last_name = request.form.get('last_name') or 'No Lname'
        return f'<a href="/form">Form</a> FirstName: {first_name}, Last Name: {last_name}'
    return render_template('form.html')


if __name__ == '__main__':
    app.run()
