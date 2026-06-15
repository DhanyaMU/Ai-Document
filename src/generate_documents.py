
"""
Document Generator - Creates realistic fake documents for testing
Run this file to generate sample documents in the sample_documents/ folder
"""

from faker import Faker
import random
import json
import os

fake = Faker()


def generate_drivers_license():
    name = fake.name()
    return {
        "document_type": "DRIVERS_LICENSE",
        "content": f"""
-------------------------------------------
      STATE DEPARTMENT OF MOTOR VEHICLES
           DRIVER'S LICENSE
-------------------------------------------

Full Name:        {name}
License Number:   DL-{fake.bothify('####-####-####')}
Date of Birth:    {fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%m/%d/%Y')}
Address:          {fake.address().replace(chr(10), ', ')}

Issue Date:       {fake.date_between(start_date='-5y', end_date='-1y').strftime('%m/%d/%Y')}
Expiry Date:      {fake.date_between(start_date='+1y', end_date='+5y').strftime('%m/%d/%Y')}

Class:            {random.choice(['A', 'B', 'C', 'D'])}
Restrictions:     {random.choice(['None', 'Corrective Lenses', 'Daylight Only'])}
Endorsements:     {random.choice(['None', 'Hazmat', 'Tanker', 'Double/Triple'])}

Sex:              {random.choice(['M', 'F'])}
Height:           {random.randint(5, 6)}'{random.randint(0, 11)}"
Eye Color:        {random.choice(['BRN', 'BLU', 'GRN', 'HZL'])}

-------------------------------------------
This license is property of the State DMV.
Must be carried while operating a motor vehicle.
-------------------------------------------
"""
    }


def generate_passport():
    name = fake.name()
    return {
        "document_type": "PASSPORT",
        "content": f"""
+--------------------------------------+
|         UNITED STATES OF AMERICA      |
|              PASSPORT                  |
+--------------------------------------+

Surname:          {name.split()[-1].upper()}
Given Names:      {name.split()[0].upper()}
Nationality:      {fake.country()}

Passport No:      {fake.bothify('??#######').upper()}
Date of Birth:    {fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%d %b %Y')}
Sex:              {random.choice(['M', 'F'])}
Place of Birth:   {fake.city()}, {fake.state()}

Date of Issue:    {fake.date_between(start_date='-8y', end_date='-1y').strftime('%d %b %Y')}
Date of Expiry:   {fake.date_between(start_date='+1y', end_date='+8y').strftime('%d %b %Y')}
Issuing Authority: U.S. Department of State

Machine Readable Zone:
P<USA{name.split()[-1].upper()}<<{name.split()[0].upper()}<<<<<<<<<<<<<<<

+--------------------------------------+
|  This document is government property |
+--------------------------------------+
"""
    }


def generate_insurance_certificate():
    company = fake.company()
    return {
        "document_type": "INSURANCE_CERTIFICATE",
        "content": f"""
+--------------------------------------+
|     CERTIFICATE OF INSURANCE          |
|     Commercial Auto Policy            |
+--------------------------------------+

Insurance Company:    {random.choice(['State Farm', 'GEICO', 'Progressive', 'Allstate', 'Liberty Mutual'])}
Policy Number:        POL-{fake.bothify('###-###-####')}

NAMED INSURED:
Name:                 {company}
DBA:                  {company} Trucking LLC
Address:              {fake.address().replace(chr(10), ', ')}

POLICY PERIOD:
Effective Date:       {fake.date_between(start_date='-1y', end_date='-1m').strftime('%m/%d/%Y')}
Expiration Date:      {fake.date_between(start_date='+1m', end_date='+1y').strftime('%m/%d/%Y')}

COVERAGES:
- Bodily Injury:        ${random.choice(['500,000', '1,000,000', '2,000,000'])} per occurrence
- Property Damage:      ${random.choice(['100,000', '250,000', '500,000'])} per occurrence
- Cargo Coverage:       ${random.choice(['50,000', '100,000', '250,000'])}
- Combined Single Limit: ${random.choice(['1,000,000', '2,000,000', '5,000,000'])}

VEHICLES COVERED:       {random.randint(1, 25)} vehicles
DRIVERS COVERED:        {random.randint(1, 40)} drivers

Certificate Holder:     Amazon Relay Transportation

+--------------------------------------+
|  AUTHORIZED REPRESENTATIVE            |
|  Signature: [SIGNED]                  |
|  Date: {fake.date_between(start_date='-30d', end_date='today').strftime('%m/%d/%Y')}                       |
+--------------------------------------+
"""
    }


def generate_compliance_form():
    company = fake.company()
    return {
        "document_type": "COMPLIANCE_FORM",
        "content": f"""
==========================================
FEDERAL MOTOR CARRIER SAFETY ADMINISTRATION
CARRIER COMPLIANCE VERIFICATION FORM
==========================================

SECTION A: CARRIER INFORMATION
-----------------------------------------
Carrier Name:         {company}
USDOT Number:         {fake.bothify('#######')}
MC Number:            MC-{fake.bothify('######')}
EIN:                  {fake.bothify('##-#######')}

SECTION B: OPERATING AUTHORITY
-----------------------------------------
Authority Type:       {random.choice(['Common', 'Contract', 'Broker', 'Freight Forwarder'])}
Authority Status:     {random.choice(['Active', 'Active - Conditional', 'Under Review'])}
Interstate:           {random.choice(['Yes', 'No'])}
Intrastate:           {random.choice(['Yes', 'No'])}

SECTION C: SAFETY RECORD
-----------------------------------------
Total Inspections (12 mo):    {random.randint(5, 100)}
Out-of-Service Rate:          {random.uniform(0, 35):.1f}%
Crash Rate (per million mi):  {random.uniform(0, 3):.2f}
Driver Fitness Violations:    {random.randint(0, 15)}
HOS Violations:               {random.randint(0, 25)}
Vehicle Maintenance Violations: {random.randint(0, 20)}

SECTION D: COMPLIANCE STATUS
-----------------------------------------
Overall Rating:       {random.choice(['Satisfactory', 'Conditional', 'Unsatisfactory'])}
Last Review Date:     {fake.date_between(start_date='-2y', end_date='-1m').strftime('%m/%d/%Y')}
Next Review Due:      {fake.date_between(start_date='+1m', end_date='+1y').strftime('%m/%d/%Y')}

CERTIFICATION: I certify that the information provided
is true and accurate to the best of my knowledge.

Signed: {fake.name()}, Compliance Officer
Date:   {fake.date_between(start_date='-30d', end_date='today').strftime('%m/%d/%Y')}
==========================================
"""
    }


def generate_vehicle_registration():
    return {
        "document_type": "VEHICLE_REGISTRATION",
        "content": f"""
+--------------------------------------+
|    DEPARTMENT OF MOTOR VEHICLES        |
|    VEHICLE REGISTRATION CERTIFICATE    |
+--------------------------------------+

Registration No:      {fake.bothify('???-####').upper()}
VIN:                  {fake.bothify('#?#??##?#??######').upper()}

VEHICLE INFORMATION:
- Year:             {random.randint(2018, 2025)}
- Make:             {random.choice(['Freightliner', 'Kenworth', 'Peterbilt', 'Volvo', 'International'])}
- Model:            {random.choice(['Cascadia', 'T680', '579', 'VNL', 'LT'])}
- Type:             {random.choice(['Tractor', 'Straight Truck', 'Semi-Trailer'])}
- Color:            {random.choice(['White', 'Black', 'Silver', 'Red', 'Blue'])}
- GVWR:             {random.choice(['26,001', '33,000', '80,000'])} lbs
- Fuel Type:        {random.choice(['Diesel', 'CNG', 'Electric'])}

REGISTERED OWNER:
Name:                 {fake.company()} Trucking Inc.
Address:              {fake.address().replace(chr(10), ', ')}

REGISTRATION PERIOD:
Effective:            {fake.date_between(start_date='-1y', end_date='-1m').strftime('%m/%d/%Y')}
Expires:              {fake.date_between(start_date='+1m', end_date='+1y').strftime('%m/%d/%Y')}

Plate Number:         {fake.bothify('???-####').upper()}
State:                {fake.state()}

+--------------------------------------+
|  VALID ONLY WITH CURRENT PLATES       |
+--------------------------------------+
"""
    }


# ============================================================
# MAIN: Generate and save documents
# ============================================================

if __name__ == "__main__":
    print("Generating sample documents...\n")

    generators = {
        "drivers_license": generate_drivers_license,
        "passport": generate_passport,
        "insurance_certificate": generate_insurance_certificate,
        "compliance_form": generate_compliance_form,
        "vehicle_registration": generate_vehicle_registration,
    }

    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_documents")
    os.makedirs(output_dir, exist_ok=True)

    all_docs = []

    for doc_name, generator in generators.items():
        for i in range(10):  # 10 of each type = 50 total
            doc = generator()
            filename = f"{doc_name}_{i+1:02d}.txt"
            filepath = os.path.join(output_dir, filename)

            # Save as text file - UTF-8 encoding to handle all characters
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc['content'])

            all_docs.append({
                "filename": filename,
                "document_type": doc['document_type'],
                "content": doc['content']
            })

    # Save metadata as JSON
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, indent=2)

    print(f"Generated {len(all_docs)} documents!")
    print(f"Saved to: {output_dir}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"\nBreakdown:")
    for doc_name in generators:
        print(f"   - {doc_name}: 10 documents")
