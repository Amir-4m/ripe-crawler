import ipaddress
import json
import logging

import requests
from bs4 import BeautifulSoup
from django.utils.encoding import force_text

logger = logging.getLogger(__name__)


class RipeCrawler(object):
    def __init__(self):
        self.organizations_list_url = 'https://www.ripe.net/membership/indices/IR.html'
        self.organization_addresses_url = "https://rest.db.ripe.net/search.json?query-string=%s&type-filter=organisation&flags=no-referenced&flags=no-irt&source=RIPE"
        self.organization_inet_url = "https://rest.db.ripe.net/search.json?query-string=%s&inverse-attribute=org&type-filter=inetnum&flags=no-referenced&flags=no-irt&source=RIPE"
        self.country = "IRAN, ISLAMIC REPUBLIC OF"

    def get_organizations_name_list(self):
        """
        return list of organizations names based on referred country.
        """
        response = requests.get(self.organizations_list_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        list_div = soup.find('div', id='external')
        organizations_names = []
        for name in list_div.findChildren("li"):
            if 'Registry Based' in name.text:
                continue
            organizations_names.append(name.text.strip())
        return organizations_names

    def get_organization_org_ids(self):
        """
        return a set of org ids that belong to an organization
        """
        organizations_names = self.get_organizations_name_list()
        ids = set()
        for name in organizations_names:
            try:
                response = requests.get(self.organization_addresses_url % name)
                orgs = json.loads(force_text(response.content))['objects']['object']
            except Exception as e:
                logger.error(f"could not fetch organization address for name {name}: {e}")
                continue

            for org in orgs:
                try:
                    attrs = org['attributes']['attribute']
                    if attrs[7]['value'] == self.country or attrs[6]['value'] == self.country:
                        ids.add(org['primary-key']['attribute'][0]['value'])
                except Exception as e:
                    logger.error(f"could not fetch organization id for {org}: {e}")
                    continue
        return ids

    def get_organization_ip_range(self):
        """
        return a set of ip subnet that belongs to each organization
        """
        org_ids = self.get_organization_org_ids()
        ranges = set()
        for org_id in org_ids:
            try:
                response = requests.get(self.organization_inet_url % org_id)
                inets = json.loads(force_text(response.content))['objects']['object']
            except Exception as e:
                logger.error(f"could not fetch org_id {org_id} : {e}")
                continue

            for inet in inets:
                try:
                    ip_range = inet['primary-key']['attribute'][0]['value'].split(' - ')
                    ip1 = ipaddress.ip_address(ip_range[0])
                    ip2 = ipaddress.ip_address(ip_range[1])
                    ranges.add(list(ipaddress.summarize_address_range(ip1, ip2))[0])
                except Exception as e:
                    logger.error(f"could not fetch range for inet {inet} and org_id {org_id} : {e}")
                    continue
        return ranges
