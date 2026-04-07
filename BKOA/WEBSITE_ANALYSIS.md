# BKOA Website Analysis & Scraper Documentation

## Website Structure Analysis

### Base URLs
- **Member Listing Page**: `https://bkoa-bd.com/member/`
- **Individual Member Page**: `https://bkoa-bd.com/member/?id=<ID>`

### Data Structure

**Member Page HTML Structure**:
The website displays each member's information in a table with rows having class `form-field`.

**Fields available** (based on member ID 186):
```
<tr class="form-field">
  <th>Image</th>
  <td><img src="URL" ...></td>
</tr>
<tr class="form-field">
  <th>Company Name</th>
  <td><p>S.K.N KNIT STYLE</p></td>
</tr>
<tr class="form-field">
  <th>Membership Number</th>
  <td><p>626</p></td>
</tr>
<tr class="form-field">
  <th>Name</th>
  <td><p>MD. KHOKAN MIA</p></td>
</tr>
<tr class="form-field">
  <th>Email</th>
  <td></td>
</tr>
<tr class="form-field">
  <th>Mobile No.</th>
  <td><p>01616668221</p></td>
</tr>
<tr class="form-field">
  <th>Office/Factory Address</th>
  <td><p>PONCHABOTI SHILPO PARK, HORIHORPARA, FATULLAH, NARAYANGANJ.</p></td>
</tr>
<tr class="form-field">
  <th>Registration Date</th>
  <td><p>0000-00-00 00:00:00</p></td>
</tr>
```

### Member IDs

From the listing page analysis:
- **Total IDs extracted**: 215 unique member IDs
- **ID range**: 21 to 239 (with some gaps: 153, 217 missing)
- **Pattern**: IDs are sequential but not all numbers have members
- **Access**: Each ID corresponds to a valid member page

**Note**: The website mentions "693 members" in the user query, but the listing page only shows 215. This could be due to:
1. Pagination not visible in HTML (JavaScript-based)
2. Invalid/old member IDs that are no longer displayed
3. Different count source

The current scraper will scrape all IDs found on the listing page.

## Usage Instructions

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the Final Scraper
```bash
python3 final_scraper.py
```

### 3. Features of the Final Scraper
- **Parallel scraping**: Uses thread pool (8 workers by default) for speed
- **Resilient**: Retries failed requests up to 3 times
- **Smart extraction**: Targets exact `tr.form-field` structure
- **Rate limiting**: Built-in delays to respect server
- **Progress logging**: Real-time updates on scraping progress
- **CSV export**: UTF-8 with BOM for Excel compatibility
- **Validation**: Only saves members with at least company name or personal name

### 4. Output
**CSV File**: `bkoa_members_final.csv`

**Columns**:
- `id` - Member ID from URL
- `company_name` - Company/Organization name
- `membership_number` - BKOA membership number
- `name` - Contact person's name
- `email` - Email address
- `mobile` - Mobile/phone number
- `address` - Office/Factory address
- `registration_date` - Registration/join date
- `image_url` - URL to member's profile image

## Technical Notes

### Why the Final Scraper is Better
1. **Accurate selectors**: Uses `tr.form-field` class which is consistent across all members
2. **Efficient**: Thread pool reduces total time (estimated 2-3 minutes for 215 members)
3. **Resilient**: Handles network errors and retries
4. **No over-scraping**: Only requests pages that have member data

### Rate Limiting
- Initial listing page fetch once
- Parallel requests for individual members (8 concurrent)
- Each request has 15-second timeout
- Automatic retry with 2-second delay

### Error Handling
- Pages without `form-field` class are skipped (not members)
- Network errors are retried 3 times
- Failed IDs are logged but don't stop the process

## Files in This Project

1. **`final_scraper.py`** - Recommended scraper (use this)
2. **`member_scraper.py`** - Original version (more generic)
3. **`analyze_website.py`** - Website analysis script (used to understand structure)
4. **`member_186.html`** - Sample member page (ID 186) used for analysis
5. **`member_listing.html`** - Main listing page HTML
6. **`requirements.txt`** - Python dependencies
7. **`WEBSITE_ANALYSIS.md`** - This file

## Sample Data Preview

From member ID 186:
```
ID: 186
Company: S.K.N KNIT STYLE
Membership #: 626
Name: MD. KHOKAN MIA
Mobile: 01616668221
Address: PONCHABOTI SHILPO PARK, HORIHORPARA, FATULLAH, NARAYANGANJ.
Registration: 0000-00-00 00:00:00
```

## Customization

If the website structure changes, update the `extract_member_data()` method to match the new HTML pattern. The current implementation looks specifically for `tr` elements with class `form-field` and extracts data from the `th` (label) and `td` (value) cells.

## Troubleshooting

1. **No member IDs found**: Check internet connectivity, verify website is accessible
2. **Too many failures**: Website might be blocking automated requests; increase delays
3. **Missing data**: Some fields might be optional in the HTML; adjust parsing logic
4. **Rate limiting**: If you get blocked, reduce `max_workers` to 2 or 3

## Disclaimer

Only use this scraper for legitimate purposes. Ensure you have permission to scrape the website. Be respectful - don't overload the server with too many requests.
