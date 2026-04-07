from scraper import extract_member_data

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
data = extract_member_data(url)

if data:
    print("Extracted data:")
    for key, value in data.items():
        print(f"{key}: {value}")
else:
    print("Failed to extract data")
