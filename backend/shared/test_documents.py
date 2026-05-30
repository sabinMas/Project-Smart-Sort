"""
Comprehensive test documents from various industries.
Use these to test email ingestion and classification across different sectors.
"""

from datetime import datetime
from backend.shared.types import IngestedDocument, ClassificationResult

# ============================================
# LAW FIRM DOCUMENTS
# ============================================

MOCK_INGESTED_LEGAL_NDA = IngestedDocument(
    id="doc-legal-nda-001",
    filename="NDA_Partnership_2024.pdf",
    content="""NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of March 1, 2024,
between Confidential Technologies Inc. ("Disclosing Party") and Innovation Partners LLC
("Receiving Party").

WHEREAS, the Disclosing Party desires to disclose certain confidential information
to the Receiving Party for the purpose of exploring a potential business partnership.

1. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means all non-public, proprietary information disclosed by
the Disclosing Party, including but not limited to: business plans, technical data,
trade secrets, customer lists, financial information, and product roadmaps.

2. OBLIGATIONS OF RECEIVING PARTY
The Receiving Party agrees to:
a) Maintain the confidentiality of all Confidential Information
b) Not disclose Confidential Information to any third party without written consent
c) Use Confidential Information only for the stated purpose
d) Return or destroy all Confidential Information upon termination

3. EXCEPTIONS
This Agreement does not apply to information that is:
a) Publicly available through no breach of this Agreement
b) Independently developed without use of Confidential Information
c) Required to be disclosed by law or court order

4. TERM
This Agreement shall remain in effect for two (2) years from the date first written above.

5. GOVERNING LAW
This Agreement shall be governed by the laws of New York, without regard to conflicts
of law principles.

IN WITNESS WHEREOF, the parties execute this Agreement:

Confidential Technologies Inc.
By: _________________________
Name: John Smith
Title: CEO
Date: March 1, 2024

Innovation Partners LLC
By: _________________________
Name: Sarah Johnson
Title: Managing Partner
Date: March 1, 2024

Witnessed by:
_________________________
Attorney at Law
State Bar #: 123456""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 1, 9, 15, 0),
    source="email",
    email_from="legal@confidentialtech.com",
    file_size_bytes=125678,
)

MOCK_INGESTED_LITIGATION_BRIEF = IngestedDocument(
    id="doc-legal-brief-001",
    filename="Plaintiff_Motion_Brief_Case_2024_CV_45678.pdf",
    content="""IN THE DISTRICT COURT OF COOK COUNTY, ILLINOIS

Case No: 2024 CV 45678

PLAINTIFF'S MOTION FOR SUMMARY JUDGMENT

Plaintiff Corporation, a Delaware Corporation
v.
Defendant Manufacturing Inc., a Illinois Corporation

TO THE HONORABLE COURT AND ALL COUNSEL OF RECORD:

Plaintiff Corporation ("Plaintiff") respectfully submits this Motion for Summary
Judgment, arguing that there exists no genuine dispute as to any material fact and
that Plaintiff is entitled to judgment as a matter of law.

FACTS:

1. Plaintiff is a corporation specializing in industrial equipment sales.
2. Defendant is a manufacturing firm located in Chicago, Illinois.
3. On June 15, 2023, Plaintiff and Defendant entered into a Purchase Agreement
   ("Agreement") for 500 units of industrial equipment.
4. The total contract value was $2,500,000.
5. Plaintiff delivered all goods on September 1, 2023.
6. Defendant has failed to pay the agreed-upon amount.

LEGAL ARGUMENT:

Plaintiff has fully performed all obligations under the Agreement. Defendant's
refusal to pay constitutes a material breach. Under Illinois law, when one party
fully performs and the other party fails to perform, summary judgment is appropriate.

The undisputed facts demonstrate:
- Contract execution (Exhibit A)
- Delivery of goods (Exhibit B - shipping documents)
- Invoice for $2,500,000 (Exhibit C)
- Non-payment (Exhibit D - demand letter)

WHEREFORE, Plaintiff respectfully requests that this Court grant this Motion for
Summary Judgment and enter judgment in favor of Plaintiff in the amount of
$2,500,000 plus interest and costs.

Respectfully submitted,

_________________________
Thompson & Associates LLP
Attorney for Plaintiff
Illinois Bar #: 654321
Date: February 15, 2024""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 2, 15, 14, 30, 0),
    source="email",
    email_from="litigation@thompsonlaw.com",
    file_size_bytes=89456,
)

# ============================================
# ACCOUNTING & TAX DOCUMENTS
# ============================================

MOCK_INGESTED_TAX_RETURN = IngestedDocument(
    id="doc-tax-1040-001",
    filename="2023_1040_Form_John_Doe.pdf",
    content="""FORM 1040: U.S. INDIVIDUAL INCOME TAX RETURN

Name: John Michael Doe
Social Security Number: ***-**-1234
Address: 5432 Oak Street, Denver, CO 80202

Filing Status: Married Filing Jointly
Spouse Name: Jane Marie Doe
Spouse SSN: ***-**-5678

Tax Year: 2023
Filing Date: March 15, 2024

INCOME SECTION:

1. Wages, salaries, tips (from W-2):
   John's W-2 (Acme Corp): $85,000
   Jane's W-2 (Healthcare Inc.): $92,500
   Total Wages: $177,500

2. Interest Income: $2,345
3. Dividend Income (Qualified): $1,890
4. Capital Gains (Long-term): $5,600
5. Self-employment Income: $12,000
6. Other Income: $0

TOTAL INCOME: $199,335

ADJUSTMENTS:

- Student Loan Interest Deduction: $2,500
- IRA Contribution: $7,000

ADJUSTED GROSS INCOME (AGI): $189,835

DEDUCTIONS:

Standard Deduction: $27,700

TAXABLE INCOME: $162,135

CREDITS:

- Child Tax Credit (2 children): $4,000
- Earned Income Tax Credit: $0
- Lifetime Learning Credit: $2,000

TOTAL TAX: $19,456
Federal Income Tax Withheld: $22,100
Estimated Tax Payments: $0

AMOUNT DUE: $0
REFUND DUE: $2,644

Prepared by:
Davis & Associates CPA Firm
CPA License #: 98765
Signature: _________________________
Date: March 1, 2024""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 1, 10, 0, 0),
    source="email",
    email_from="tax@davisaccounting.com",
    file_size_bytes=145670,
)

MOCK_INGESTED_AUDIT_REPORT = IngestedDocument(
    id="doc-audit-report-001",
    filename="FY2023_Audit_Report_TechCorp_Inc.pdf",
    content="""INDEPENDENT AUDITOR'S REPORT

To the Board of Directors and Stockholders of TechCorp Inc.

We have audited the accompanying consolidated financial statements of TechCorp Inc.
and subsidiaries as of December 31, 2023 and 2022, and for the years then ended.

OPINION:

In our opinion, the financial statements present fairly, in all material respects,
the financial position of TechCorp Inc. and subsidiaries as of December 31, 2023
and 2022, and the results of their operations and their cash flows for the years
then ended in accordance with Generally Accepted Accounting Principles (GAAP).

AUDITOR RESPONSIBILITIES:

Our responsibility is to express an opinion on these financial statements based on
our audits. We are a public accounting firm registered with the Public Company
Accounting Oversight Board (PCAOB).

We conducted our audits in accordance with the standards of the PCAOB. Those
standards require that we plan and perform the audit to obtain reasonable assurance
about whether the financial statements are free of material misstatement.

FINANCIAL STATEMENT SUMMARY:

As of December 31, 2023:
- Total Assets: $487,650,000
- Total Liabilities: $189,340,000
- Stockholders' Equity: $298,310,000

For the Year Ended December 31, 2023:
- Total Revenue: $652,000,000
- Operating Income: $89,300,000
- Net Income: $61,450,000
- Earnings Per Share (Basic): $2.45
- Earnings Per Share (Diluted): $2.38

MATERIAL FINDINGS:

1. Revenue Recognition: We noted adequate controls over revenue recognition
   consistent with ASC 606.
2. Accounts Receivable: Allowance for doubtful accounts is reasonable at $4.2M.
3. Inventory: Physical inventory counts performed 12/15/2023 reconcile to records.

AUDIT OPINION:

In our opinion, the financial statements are fairly presented and we have no
material weaknesses in internal controls to report.

Respectfully submitted,

_________________________
Ernst & Young LLP
Certified Public Accountants
License #: LIC-2024-456
Engagement Partner: Robert Chen, CPA
Audit Date: February 20, 2024""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 2, 20, 11, 45, 0),
    source="email",
    email_from="audit@ey.com",
    file_size_bytes=267890,
)

MOCK_INGESTED_W2_FORM = IngestedDocument(
    id="doc-w2-form-001",
    filename="2023_W2_Jane_Doe_Healthcare_Inc.pdf",
    content="""FORM W-2: WAGE AND TAX STATEMENT
Tax Year: 2023

Box a: Employee's SSN: ***-**-5678
Box b: Employer's EIN: 45-6789012

Employee Name: Jane Marie Doe
Address: 5432 Oak Street, Denver, CO 80202

Employer Name: Healthcare Inc.
Employer Address: 8900 Medical Plaza Drive, Denver, CO 80210

Box 1: Wages, tips, other compensation: $92,500.00
Box 2: Federal income tax withheld: $14,200.00
Box 3: Social security wages: $92,500.00
Box 4: Social security tax withheld: $5,735.00
Box 5: Medicare wages and tips: $92,500.00
Box 6: Medicare tax withheld: $1,341.25
Box 12a: Code D: $6,200.00 (401k contributions)
Box 19: Employer's state ID: CO-123456
Box 20: State income tax withheld: $4,625.00

Employer Contact:
HR Department: hr@healthcareinc.com
Phone: (303) 555-0100

Prepared by: Healthcare Inc. Payroll Services
Date: January 31, 2024
Authorized Signature: _________________________
Title: Payroll Manager""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 1, 31, 8, 30, 0),
    source="email",
    email_from="payroll@healthcareinc.com",
    file_size_bytes=45670,
)

# ============================================
# FINANCIAL SERVICES DOCUMENTS
# ============================================

MOCK_INGESTED_BANK_STATEMENT = IngestedDocument(
    id="doc-bank-statement-001",
    filename="2024_Q1_Business_Account_Statement.pdf",
    content="""BANK OF AMERICA - BUSINESS CHECKING ACCOUNT
Statement Period: March 1, 2024 - March 31, 2024

Account Holder: Innovation Enterprises LLC
Account Number: ****6789
Routing Number: 121000248

ACCOUNT SUMMARY:

Beginning Balance: $245,678.90
Total Deposits: $487,900.00
Total Withdrawals: ($392,450.00)
Interest Earned: $125.32
Ending Balance: $341,254.22

DEPOSITS:

3/1/2024: Direct Deposit - Salary Processing: $12,500.00
3/5/2024: Client Payment - Project XYZ: $125,000.00
3/8/2024: ACH Transfer - Consulting Income: $45,000.00
3/12/2024: Wire Transfer - Refund from Vendor: $80,000.00
3/15/2024: Check Deposit - Client Invoice #2847: $95,400.00
3/20/2024: ACH Transfer - Interest Income: $130,000.00

WITHDRAWALS:

3/2/2024: Check #1001 - Payroll Expenses: ($25,000.00)
3/5/2024: ACH Debit - Rent Payment: ($8,500.00)
3/7/2024: Wire Transfer - Vendor Payment: ($75,000.00)
3/10/2024: Check #1002 - Office Supplies: ($2,450.00)
3/15/2024: ACH Debit - Utilities: ($3,200.00)
3/20/2024: Wire Transfer - Loan Payment: ($150,000.00)
3/28/2024: Check #1003 - Insurance: ($128,300.00)

SERVICE FEES: $0.00 (Waived - Premium Account)

DAILY BALANCES:
3/1: $245,678.90
3/5: $340,128.90
3/10: $335,128.90
3/15: $427,528.90
3/20: $407,528.90
3/31: $341,254.22

Account Status: ACTIVE - No issues

Questions? Contact: 1-800-BANK-USA""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 4, 5, 9, 0, 0),
    source="email",
    email_from="statements@bankofamerica.com",
    file_size_bytes=78900,
)

MOCK_INGESTED_LOAN_DOCUMENT = IngestedDocument(
    id="doc-loan-agreement-001",
    filename="Business_Loan_Agreement_2024.pdf",
    content="""PROMISSORY NOTE AND LOAN AGREEMENT

Borrower: Growth Tech Solutions Inc.
Lender: Wells Fargo Business Capital
Loan Amount: $500,000.00
Loan Date: March 15, 2024
Maturity Date: March 15, 2029

LOAN TERMS:

Principal Amount: $500,000.00
Interest Rate: 6.75% per annum (Fixed)
Monthly Payment: $9,726.50
Number of Payments: 60
Payment Due Date: 15th of each month

BORROWER INFORMATION:

Name: Growth Tech Solutions Inc.
Type: C Corporation
EIN: 56-7890123
Principal Place of Business: 1234 Tech Drive, San Jose, CA 95110
Owner/CEO: Michael Chen
Contact: (408) 555-0123

COLLATERAL:

The Borrower pledges the following as security:
1. First Lien on Business Assets (Equipment, Inventory, Receivables)
2. Personal Guarantee from Michael Chen
3. UCC-1 Filing in California Secretary of State

REPRESENTATIONS AND WARRANTIES:

The Borrower represents and warrants:
1. Properly organized and duly authorized to conduct business
2. Has obtained all necessary approvals and consents
3. No material adverse changes in financial condition
4. No litigation pending or threatened
5. Full disclosure of all material facts

COVENANTS:

The Borrower covenants to:
1. Maintain minimum cash reserves of $50,000
2. Maintain current liability insurance of $1,000,000
3. Provide quarterly financial statements
4. Not incur additional debt exceeding $100,000 without lender approval
5. Maintain net worth of at least $250,000

DEFAULT CONDITIONS:

Payment more than 15 days late
Breach of covenants not cured within 30 days
Material adverse change in financial condition
Cross-default with other lenders

ACCELERATION:

Upon default, entire outstanding balance becomes immediately due and payable
at 10% per annum.

SIGNATURES:

Growth Tech Solutions Inc.

By: _________________________
Name: Michael Chen
Title: Chief Executive Officer
Date: March 15, 2024

Wells Fargo Business Capital

By: _________________________
Name: Jennifer Martinez
Title: Loan Officer
Date: March 15, 2024""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 15, 14, 0, 0),
    source="email",
    email_from="loans@wellsfargo.com",
    file_size_bytes=98765,
)

# ============================================
# HUMAN RESOURCES DOCUMENTS
# ============================================

MOCK_INGESTED_OFFER_LETTER = IngestedDocument(
    id="doc-offer-letter-001",
    filename="Offer_Letter_Sarah_Johnson_Senior_Engineer.pdf",
    content="""EMPLOYMENT OFFER LETTER

Date: March 20, 2024

To: Sarah Elizabeth Johnson
    2847 Maple Avenue
    Portland, OR 97214
    Email: sarah.johnson@email.com
    Phone: (503) 555-0198

Dear Sarah,

We are pleased to offer you a position as Senior Software Engineer with TechVision
Industries, effective April 15, 2024.

POSITION DETAILS:

Title: Senior Software Engineer
Department: Engineering
Reports To: Director of Engineering
Work Location: Portland, OR (Hybrid - 3 days on-site)

COMPENSATION AND BENEFITS:

Base Salary: $165,000.00 per year, payable biweekly
Performance Bonus: Up to 20% of base salary (annual, at company discretion)
Sign-on Bonus: $15,000.00 (payable first paycheck)

Benefits Package (effective May 1, 2024):
- Health Insurance: Medical, Dental, Vision (company pays 80%)
- 401(k) Plan: Company matches 4% of salary
- Paid Time Off: 20 days vacation, 10 days sick, 6 holidays
- Stock Options: 5,000 shares at $2.50/share, 4-year vesting
- Commuter Benefits: Pre-tax transit program
- Professional Development: $5,000/year for training/conferences

EMPLOYMENT TERMS:

This is an at-will employment relationship. Your employment is contingent upon:
1. Successful background check and reference verification
2. Proof of eligibility to work in the United States (Form I-9)
3. Signing of Confidentiality and Invention Assignment Agreement
4. Signing of Employee Handbook acknowledgment

At-Will Employment: Either party may terminate employment at any time with
appropriate notice.

CONFIDENTIALITY:

You will be required to sign our standard Confidentiality Agreement protecting
company trade secrets, customer information, and proprietary technology.

BACKGROUND CHECK:

This offer is contingent upon successful completion of a background check
including criminal history, employment verification, and reference checks.

ACCEPTANCE:

To accept this offer, please sign below and return by April 1, 2024.

We look forward to welcoming you to the TechVision team!

Sincerely,

_________________________
Robert Williams
Vice President, Human Resources
TechVision Industries

Phone: (503) 555-0100
Email: robert.williams@techvision.com

---ACCEPTANCE---

I accept the employment offer as stated above:

Employee Signature: _________________________
Date: _________________________""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 20, 15, 30, 0),
    source="email",
    email_from="hr@techvision.com",
    file_size_bytes=87654,
)

MOCK_INGESTED_PERFORMANCE_REVIEW = IngestedDocument(
    id="doc-perf-review-001",
    filename="2024_Q1_Performance_Review_Michael_Davis.pdf",
    content="""ANNUAL PERFORMANCE REVIEW

Employee: Michael Davis
Employee ID: EMP-2021-0847
Review Period: January 1, 2024 - December 31, 2024
Review Date: March 15, 2024
Reviewer: Patricia Moore, Senior Manager
Department: Sales & Business Development

PERFORMANCE SUMMARY:

Overall Rating: EXCEEDS EXPECTATIONS (4 of 5)

COMPETENCY RATINGS:

1. Technical Skills/Job Knowledge: EXCEEDS (4/5)
   Michael demonstrates strong technical knowledge of our product suite and
   competitive landscape. He has consistently delivered quality work.

2. Communication Skills: MEETS (3/5)
   Michael communicates effectively with customers but could improve on internal
   team communication. Recommend participating in communication workshops.

3. Team Collaboration: EXCEEDS (4/5)
   Michael works well with cross-functional teams and has mentored junior sales
   representatives effectively.

4. Leadership & Initiative: EXCEEDS (4/5)
   Michael takes ownership of projects and has proposed several process improvements.

5. Customer Service: EXCEEDS (4/5)
   Customer satisfaction scores average 4.6/5. Feedback consistently positive.

6. Attendance/Reliability: MEETS (3/5)
   Michael has had 4 unscheduled absences this year. Attendance expectations not met.

7. Sales Performance: EXCEEDS (4/5)
   FY2024 Target: $800,000 | Actual: $945,000 | 118% of target
   New client acquisition: 12 clients (target: 8)

GOALS & ACCOMPLISHMENTS:

Achieved Goals:
✓ Exceeded sales quota by 18%
✓ Brought on 4 new major enterprise accounts
✓ Reduced average sales cycle by 15 days
✓ Developed customer retention program (92% retention rate)

Partially Achieved:
◐ Completed 3 of 4 targeted professional certifications

Not Achieved:
✗ Internal mentor training program (deferred to next quarter)

DEVELOPMENT AREAS:

1. Attendance: Address unscheduled absences and maintain 95% attendance
2. Internal Communications: Take a business communication course
3. Documentation: Improve CRM data entry and documentation (currently 78% vs. 90% target)

STRENGTHS:

Michael's key strengths are:
- Exceptional sales ability and customer relationship management
- Strong product knowledge and competitive awareness
- Initiative in developing new business development strategies
- Positive attitude and customer focus

RECOMMENDATIONS FOR 2025:

1. Promote to Senior Sales Representative with $35,000 salary increase
2. Assign as mentor to two junior sales staff
3. Enroll in Leadership Development Program
4. Work with manager on attendance improvement plan

COMPENSATION DISCUSSION:

Salary Increase: 8% ($60,000 → $64,800 annually)
Bonus Target: 15% of base (increased from 12%)
Stock Options: 2,000 additional shares

EMPLOYEE ACKNOWLEDGMENT:

I have reviewed this performance evaluation and discussed it with my manager.

Employee Signature: _________________________ Date: _____________

Manager Signature: _________________________ Date: _____________

HR Signature: _________________________ Date: _____________""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 15, 16, 0, 0),
    source="email",
    email_from="hr@companyname.com",
    file_size_bytes=125670,
)

# ============================================
# REAL ESTATE & LEASE DOCUMENTS
# ============================================

MOCK_INGESTED_LEASE_AGREEMENT = IngestedDocument(
    id="doc-lease-agreement-001",
    filename="Commercial_Lease_Agreement_2024_Suite_400.pdf",
    content="""COMMERCIAL LEASE AGREEMENT

LANDLORD: Skyline Properties LLC
Address: 1000 Business Center Drive, Denver, CO 80202
Phone: (303) 555-0100

TENANT: Digital Marketing Services Inc.
Address: Current: 500 Oak Street, Suite 200, Denver, CO 80202
New Address: 1000 Business Center Drive, Suite 400, Denver, CO 80202

LEASE TERM:

Commencement Date: May 1, 2024
Initial Lease Term: 5 years (60 months)
Expiration Date: April 30, 2029

RENTAL RATES:

Year 1 (5/1/2024 - 4/30/2025): $4,500/month = $54,000/year
Year 2 (5/1/2025 - 4/30/2026): $4,650/month = $55,800/year
Year 3 (5/1/2026 - 4/30/2027): $4,800/month = $57,600/year
Year 4-5 (5/1/2027 - 4/30/2029): $4,950/month = $59,400/year

Payment Terms: Due on the 1st of each month
Late Fee: $450 if payment 5+ days late
NSF Check Fee: $35

PREMISES:

Suite Number: 400
Floor: 4th
Square Footage: 3,000 sq ft
Use: General Office (Tenant use only for digital marketing services)
Building Amenities: Lobby access, security, parking (1 space per 1000 sq ft)

OPERATING EXPENSES:

Base Year: 2024
Base Operating Costs: $6.50/sq ft = $19,500 annually
Tenant's Share: 8% of building (3,000 of 37,500 sq ft)

Operating Expenses Include:
- Building maintenance and repairs
- Property taxes
- Insurance
- Utilities (except tenant-specific)
- Common area maintenance

TENANT OBLIGATIONS:

1. Pay rent timely as specified
2. Maintain property in good condition
3. Not make alterations without landlord approval
4. Comply with all laws and regulations
5. Maintain liability insurance ($1,000,000 minimum)
6. Not sublease without landlord consent (25% of profit split)
7. Keep space clean and maintain HVAC filters monthly
8. Permit landlord inspections 48 hours notice

LANDLORD OBLIGATIONS:

1. Maintain building structure and common areas
2. Provide utilities (heating, cooling, base electricity)
3. Maintain liability and property insurance
4. Comply with building codes
5. Repair common area damage (not tenant-caused)

SECURITY DEPOSIT:

Amount: $13,500 (3 months rent)
Held By: Landlord
Interest Rate: None
Return: Within 30 days of lease end minus any deductions

TERM OPTIONS:

Renewal Option: 3-year renewal at market rate + 3%
Renewal Notice: By March 31, 2029
No automatic renewal - affirmative action required

LEASE TERMINATION:

Early Termination Fee: 5 months rent ($22,500) if before 4/30/2026
None if after 5/1/2026 (notice requirement: 60 days)

SIGNATURES:

Skyline Properties LLC

By: _________________________
Name: Jennifer Martinez
Title: Property Manager
Date: March 25, 2024

Digital Marketing Services Inc.

By: _________________________
Name: David Thompson
Title: Chief Executive Officer
Date: March 25, 2024""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 25, 13, 0, 0),
    source="email",
    email_from="leasing@skylineproperties.com",
    file_size_bytes=145678,
)

# ============================================
# PROCUREMENT & SUPPLY CHAIN DOCUMENTS
# ============================================

MOCK_INGESTED_RFP_RESPONSE = IngestedDocument(
    id="doc-rfp-response-001",
    filename="RFP_Response_Software_Development_Services_2024.pdf",
    content="""REQUEST FOR PROPOSAL (RFP) RESPONSE

Company: CloudTech Solutions LLC
Date Submitted: March 18, 2024
RFP Number: CORP-2024-0512
Project: Enterprise Software Development & Integration

EXECUTIVE SUMMARY:

CloudTech Solutions is pleased to submit this response to your RFP for Enterprise
Software Development & Integration Services. With 12 years of experience in enterprise
software solutions, our team is well-positioned to deliver a comprehensive, robust
solution that meets and exceeds your requirements.

COMPANY INFORMATION:

Legal Entity: CloudTech Solutions LLC
Years in Business: 12 years
Employees: 247 (average annual growth: 15%)
Annual Revenue (2023): $45.2M
Certifications: ISO 9001, ISO 27001, SOC 2 Type II
References: Available upon request

SOLUTION OVERVIEW:

Our proposed solution includes:
1. Custom software development using agile methodology
2. Cloud infrastructure setup and management (AWS)
3. Database design and optimization
4. API development and integration
5. Security hardening and penetration testing
6. Staff training and knowledge transfer
7. Post-launch support for 12 months

TECHNICAL APPROACH:

Technology Stack:
- Backend: Python, Node.js, Go
- Frontend: React, Vue.js
- Database: PostgreSQL, MongoDB
- Cloud Infrastructure: AWS
- CI/CD: Jenkins, GitHub Actions

Development Team:
- Project Manager: 1 (10+ years experience)
- Senior Developers: 3 (8+ years average)
- Junior Developers: 4 (2+ years average)
- QA Engineers: 2
- DevOps Engineer: 1

PROJECT TIMELINE:

Phase 1: Requirements & Design (Weeks 1-4)
Phase 2: Core Development (Weeks 5-16)
Phase 3: Integration & Testing (Weeks 17-20)
Phase 4: UAT & Deployment (Weeks 21-24)
Phase 5: Training & Handoff (Weeks 25-26)

Total Duration: 6 months

PRICING:

Development Services: $850,000
Infrastructure Setup: $125,000
License Fees (1 year): $45,000
Training & Documentation: $30,000
Support (Year 1): $50,000

TOTAL PROJECT COST: $1,100,000

Payment Schedule:
- 20% ($220,000) upon contract signature
- 30% ($330,000) at end of Phase 2
- 30% ($330,000) at end of Phase 4
- 20% ($220,000) upon go-live

SCHEDULE OF EXCEPTIONS:

Exception to Requirement #4: Our database design will use PostgreSQL instead of
Oracle. This provides equivalent functionality at 60% cost savings.

Exception to Requirement #7: Our proposed AWS infrastructure allows for auto-scaling
versus the specified fixed server capacity.

REFERENCES:

1. Acme Financial Services
   Project: Banking Platform Upgrade ($2.5M)
   Contact: John Smith, VP IT
   Email: john.smith@acmefinancial.com
   Phone: (212) 555-0198

2. RetailMax Corporation
   Project: E-commerce Platform Development ($1.8M)
   Contact: Sarah Chen, CTO
   Email: sarah.chen@retailmax.com
   Phone: (415) 555-0147

3. HealthTech Innovations
   Project: Healthcare Records System ($1.2M)
   Contact: Michael Johnson, Director of IT
   Email: michael.johnson@healthtech.com
   Phone: (617) 555-0156

TERMS & CONDITIONS:

This proposal is valid for 60 days from submission date.
Payment terms: Net 30 days from invoice
Equipment becomes client property upon delivery
All source code and documentation transfer to client at project completion

CERTIFICATION:

I certify that this proposal contains true and accurate information regarding
CloudTech Solutions and the proposed solution.

_________________________
David Richardson
CEO, CloudTech Solutions
Date: March 18, 2024
Email: david@cloudtech.com
Phone: (415) 555-0100""",
    content_type="application/pdf",
    uploaded_at=datetime(2024, 3, 18, 11, 30, 0),
    source="email",
    email_from="proposals@cloudtech.com",
    file_size_bytes=167890,
)

# ============================================
# INSURANCE & COMPLIANCE DOCUMENTS
# ============================================

MOCK_INGESTED_INSURANCE_CERTIFICATE = IngestedDocument(
    id="doc-insurance-cert-001",
    filename="Certificate_of_Insurance_2024_General_Liability.pdf",
    content="""CERTIFICATE OF INSURANCE

PRODUCER: Anderson Insurance Group
Address: 500 Commerce Street, Suite 100, Denver, CO 80202
Phone: (303) 555-0100
Email: certificates@andersoninsurance.com

INSURED: TechVision Industries Inc.
Address: 1200 Tech Center Drive, Denver, CO 80201

INSURANCE INFORMATION:

Policy Type: Commercial General Liability
Policy Number: GL-2024-456789
Effective Date: January 1, 2024
Expiration Date: December 31, 2024
Renewal Option: Yes, automatically renewed unless canceled

INSURER: Hartford Insurance Company
A+ Rating (A.M. Best)
Policy Holder: TechVision Industries Inc.

COVERAGE LIMITS:

General Liability:
- Each Occurrence: $1,000,000
- General Aggregate: $2,000,000
- Products-Completed Ops: $2,000,000
- Personal Injury: $1,000,000

Automobile Liability:
- Combined Single Limit: $1,000,000

Professional Liability:
- Per Claim: $1,000,000
- Aggregate: $2,000,000

Workers' Compensation:
- Statutory Limits per State
- Employer's Liability: $1,000,000 / $1,000,000 / $500,000

ADDITIONAL INSURED:

The following are additional insureds:
- Clients as specified in contracts
- Landlord: Skyline Properties LLC
- Lenders and Financing Sources

WAIVER OF SUBROGATION:

Waived in favor of clients as required by contract.

CANCELLATION NOTICE:

Insurer agrees to notify certificate holder of cancellation or material change
with 30 days notice (10 days for non-payment).

EVIDENCE OF COVERAGE:

This certificate is issued as a matter of information only and confers no rights
upon the certificate holder. This certificate does not affirmatively or negatively
alter, extend or change the coverage afforded by the policies below.

AUTHORIZED REPRESENTATIVE:

_________________________
Robert Martinez
Authorized Agent
Anderson Insurance Group
License #: CA-198765

Date: December 15, 2023
Certificate Valid Through: December 31, 2024""",
    content_type="application/pdf",
    uploaded_at=datetime(2023, 12, 15, 9, 0, 0),
    source="email",
    email_from="certificates@andersoninsurance.com",
    file_size_bytes=56789,
)

# ============================================
# CLASSIFICATION RESULTS FOR ALL TEST DOCUMENTS
# ============================================

MOCK_CLASSIFICATION_NDA = ClassificationResult(
    document_id="doc-legal-nda-001",
    doc_type="contract",
    confidence=0.99,
    reasoning="Document contains legal agreement terms, party obligations, confidentiality provisions, governing law clause, and signature blocks typical of NDA contracts.",
    extracted_fields={
        "document_type": "Non-Disclosure Agreement",
        "parties": ["Confidential Technologies Inc.", "Innovation Partners LLC"],
        "effective_date": "2024-03-01",
        "term": "2 years",
        "key_obligations": "Maintain confidentiality, not disclose to third parties",
    },
    required_reviewer="legal",
    metadata_tags=["contract", "legal", "nda", "confidentiality", "2024"],
    classified_at=datetime(2024, 3, 1, 9, 15, 0),
)

MOCK_CLASSIFICATION_TAX_RETURN = ClassificationResult(
    document_id="doc-tax-1040-001",
    doc_type="other",
    confidence=0.97,
    reasoning="Document is IRS Form 1040 with income sections, deductions, tax calculations, and tax professional signature. Does not fit standard document types but is clearly a tax return.",
    extracted_fields={
        "form_type": "1040",
        "taxpayer_name": "John Michael Doe",
        "filing_status": "Married Filing Jointly",
        "total_income": 199335.00,
        "total_tax": 19456.00,
        "refund_amount": 2644.00,
        "tax_year": 2023,
    },
    required_reviewer="finance",
    metadata_tags=["tax_return", "1040_form", "individual_tax", "2023", "march_2024"],
    classified_at=datetime(2024, 3, 1, 10, 0, 0),
)

MOCK_CLASSIFICATION_AUDIT_REPORT = ClassificationResult(
    document_id="doc-audit-report-001",
    doc_type="other",
    confidence=0.96,
    reasoning="Independent auditor's report with opinion on financial statements, audit findings, GAAP compliance, and auditor signature. Financial audit document.",
    extracted_fields={
        "audit_type": "Annual Comprehensive Audit",
        "company_audited": "TechCorp Inc.",
        "fiscal_year": 2023,
        "total_assets": 487650000.00,
        "net_income": 61450000.00,
        "auditor": "Ernst & Young LLP",
        "opinion": "Unqualified",
    },
    required_reviewer="finance",
    metadata_tags=["audit_report", "financial", "ey", "fy2023", "unqualified_opinion"],
    classified_at=datetime(2024, 2, 20, 11, 45, 0),
)

MOCK_CLASSIFICATION_OFFER_LETTER = ClassificationResult(
    document_id="doc-offer-letter-001",
    doc_type="other",
    confidence=0.95,
    reasoning="Employment offer letter with job title, compensation, benefits, conditions, and acceptance signature block typical of HR offer documents.",
    extracted_fields={
        "employee_name": "Sarah Elizabeth Johnson",
        "position": "Senior Software Engineer",
        "start_date": "2024-04-15",
        "salary": 165000.00,
        "sign_on_bonus": 15000.00,
        "bonus_target": "20%",
    },
    required_reviewer="hr",
    metadata_tags=["offer_letter", "employment", "hr", "senior_engineer", "april_2024"],
    classified_at=datetime(2024, 3, 20, 15, 30, 0),
)

MOCK_CLASSIFICATION_LEASE = ClassificationResult(
    document_id="doc-lease-agreement-001",
    doc_type="contract",
    confidence=0.98,
    reasoning="Commercial lease agreement with landlord/tenant information, rental rates, term dates, obligations, security deposit, and signature blocks.",
    extracted_fields={
        "property_address": "1000 Business Center Drive, Denver, CO 80202",
        "unit": "Suite 400",
        "square_footage": 3000,
        "lease_term": "5 years",
        "start_date": "2024-05-01",
        "end_date": "2029-04-30",
        "annual_rent_year1": 54000.00,
    },
    required_reviewer="legal",
    metadata_tags=["lease_agreement", "commercial_real_estate", "5_year_term", "denver"],
    classified_at=datetime(2024, 3, 25, 13, 0, 0),
)

MOCK_CLASSIFICATION_RFP = ClassificationResult(
    document_id="doc-rfp-response-001",
    doc_type="other",
    confidence=0.94,
    reasoning="RFP response document with company information, solution overview, technical approach, pricing, timeline, and authorized signature.",
    extracted_fields={
        "company": "CloudTech Solutions LLC",
        "rfp_number": "CORP-2024-0512",
        "project": "Enterprise Software Development & Integration",
        "total_cost": 1100000.00,
        "duration_months": 6,
        "submitted_date": "2024-03-18",
    },
    required_reviewer="procurement",
    metadata_tags=["rfp_response", "procurement", "software_development", "1.1M_contract"],
    classified_at=datetime(2024, 3, 18, 11, 30, 0),
)
