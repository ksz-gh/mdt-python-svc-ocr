def parse_ssm_content(text_lines):
    extracted = {
        "company_name": "Not Found",
        "registration_no": "Not Found",
        "incorporation_date": "Not Found",
        "business_address": "Not Found",
        "district": "Not Found",
        "state": "Not Found",
        "country": "Not Found",
        "postcode": "Not Found",
        "nature_of_business": "Not Found",
    }

    if not text_lines:
        return extracted

    for i, line in enumerate(text_lines):
        if not isinstance(line, str): continue
        clean = line.strip().upper()

        # 1. Company Name
        if clean == "NAME" or clean == ":NAME":
            if i + 1 < len(text_lines):
                extracted["company_name"] = str(text_lines[i+1]).lstrip(':').strip()

        # 2. Registration No
        if "REGISTRATION NO." in clean:
            if i + 1 < len(text_lines):
                extracted["registration_no"] = str(text_lines[i+1]).lstrip(':').strip()

        # 3. Incorporation Date
        if "INCORPORATION DATE" in clean:
            if i + 1 < len(text_lines):
                extracted["incorporation_date"] = str(text_lines[i+1]).lstrip(':').strip()

        # 4. Business Address
        if "BUSINESS ADDRESS" in clean:
            address_parts = []
            curr = i + 1
            while curr < len(text_lines):
                val = str(text_lines[curr]).strip()
                if "POSTCODE" in val.upper():
                    if curr + 1 < len(text_lines):
                        extracted["postcode"] = str(text_lines[curr+1]).lstrip(':').strip()
                    break
                if len(val) > 2:
                    address_parts.append(val.lstrip(':').strip())
                curr += 1

            if len(address_parts) >= 2:
                extracted["state"] = address_parts[-1]
                extracted["district"] = address_parts[-2]
                extracted["business_address"] = ", ".join(address_parts[:-2])
            elif len(address_parts) == 1:
                extracted["business_address"] = address_parts[0]

        # 6. Nature of Business
        if "NATURE OF BUSINESS" in clean:
            nature_parts = []
            for j in range(i + 1, len(text_lines)):
                val = str(text_lines[j]).strip()
                if any(m in val.upper() for m in ["SCMI", "MY2507", "USER ID"]): break
                nature_parts.append(val.lstrip(':').strip())
            extracted["nature_of_business"] = " ".join(nature_parts)

        # 7. Origin
        if "ORIGIN" in clean:
            if i + 1 < len(text_lines):
                extracted["country"] = str(text_lines[i+1]).lstrip(':').strip()

    return extracted