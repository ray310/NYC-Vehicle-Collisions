"""Scape NYC City Council websites for name and point of contact information."""

import argparse
import csv
import os.path
import re
import bs4
import requests
import src.utils

BASE_DISTRICTS_URL = "https://council.nyc.gov/district-"
# Selected user agent was arbitrary agent that didn't result in 403 response
# Others should work as well
SAVE_NAME = "City Council POCs.csv"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Get NYC City Council Members and Points of Contact"
    )
    parser.add_argument(
        "-s",
        "--save",
        required=True,
        help="Path to data directory where scraped data will be saved",
        metavar="",
    )
    parser.add_argument(
        "-g",
        "--geojson",
        required=True,
        help="Path to city council geojson",
        metavar="",
    )
    return parser.parse_args()


def parse_cc_member_name(text):
    """Parse text for City Council member name."""
    title_name_re = "(-{1}\\ +)(.*)"  # 1 hyphen, 1+ spaces, any non-newline
    match = re.search(title_name_re, text)
    if match:
        return match.group(2)
    return None


def format_phone_number(area_code, first, second):
    """Check if US phone number is seemingly valid and format number."""
    try:
        assert len(area_code) == 3
        assert len(first) == 3
        assert len(second) == 4
        return "-".join([str(int(x)) for x in (area_code, first, second)])
    except (AssertionError, TypeError, ValueError):
        return None


def parse_phone_number(text):
    """Parse text for phone number and perform basic validation."""
    phone_space = "(\\ *-*\\ *)"  # 0+ spaces, 0+ hyphens, 0+ spaces
    phone_pattern = (
        "(([(]*)([0-9]{3})([)]*)"
        + phone_space
        + "([0-9]{3})"
        + phone_space
        + "([0-9]{4}))"
    )
    phone_number = None
    match = re.search(phone_pattern, text)
    if match:
        area_code = match.group(3)
        first_three = match.group(6)
        last_four = match.group(8)
        phone_number = format_phone_number(area_code, first_three, last_four)
    return phone_number


def parse_address(text):
    """Parse text for district office address."""
    address = None
    newline = "(\n|\r\n)+"
    address_pattern = (
        "(.+)" + newline + "(.+)" + newline + "(.+)"  # optional third line
    )
    match = re.search(address_pattern, text)
    if match:
        address = match.group(1).strip()
        if len(match.group(3)) > 0:
            address += "\n" + match.group(3).strip()
        phone_number = parse_phone_number(match.group(5))
        if not phone_number:  # if not phone number, then part of address
            address += "\n" + match.group(5).strip()
    return address


def parse_cc_email(email_tag, district_num):
    """Parse text for district email."""
    email = f"district{district_num}@council.nyc.gov"
    if email_tag is None:
        return email
    text = email_tag["href"]
    email_pattern = "(mailto:)(.+@council.nyc.gov)"
    match = re.search(email_pattern, text)
    if match:
        email = match.group(2)
    return email


def request_district_page(district_num, headers):
    """Request and return district page."""
    url = BASE_DISTRICTS_URL + str(district_num)
    return requests.request("get", url, headers=headers, timeout=60)


def scrape_district_info(district_num: int, districts_info: dict):
    """Query City Council District page and parse info."""
    district_info = {
        "District Number": district_num,
        "Council Member": None,
        "District Office Address": None,
        "District Office Phone": None,
        "District Email": None,
    }

    # Not including user-agent led to 403 response
    headers_dict = {"user-agent": USER_AGENT}
    response = request_district_page(district_num, headers_dict)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # council member name
        district_info["Council Member"] = parse_cc_member_name(soup.title.text)

        # get phone number and address for district office
        address_phone_tag_attrs = {"aria-label": "District office contact information"}
        address_phone_div = soup.find(name="div", attrs=address_phone_tag_attrs)
        district_info["District Office Address"] = parse_address(
            address_phone_div.p.text
        )
        district_info["District Office Phone"] = parse_phone_number(
            address_phone_div.p.text
        )

        # district email
        email_tag = soup.find("a", attrs={"aria-label": True, "href": True})
        district_info["District Email"] = parse_cc_email(email_tag, district_num)

    districts_info[district_num] = district_info


def scrape_cc_districts_info(args):
    """Script driver."""
    district_nums, _ = src.utils.read_geojson(args.geojson, "coun_dist")
    district_nums = [int(x) for x in district_nums]
    districts_contact_info = {}  # key is district number
    for district_num in sorted(district_nums):
        scrape_district_info(district_num, districts_contact_info)

    with open(os.path.join(args.save, SAVE_NAME), "w+", encoding="utf-8") as fp:
        fieldnames = [
            "District Number",
            "Council Member",
            "District Office Address",
            "District Office Phone",
            "District Email",
        ]
        writer = csv.DictWriter(fp, fieldnames=fieldnames, dialect="unix")
        writer.writeheader()
        for _, rowdict in sorted(districts_contact_info.items()):
            writer.writerow(rowdict)


if __name__ == "__main__":
    scrape_cc_districts_info(parse_args())
