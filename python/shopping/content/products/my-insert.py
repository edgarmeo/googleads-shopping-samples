from __future__ import print_function
import sys

from numpy import product

# The common module provides setup functionality used by the samples,
# such as authentication and unique id generation.
from shopping.content import common
from woocommerce import API

import json

import requests


def get_all_product(api_client,api_secret,pim_token,pim_username,pim_pwd,pim_url):
    def get_pim_access_token():
        headers={
            "Content-Type" : "application/json",
            "Authorization" : f"Basic {pim_token}"
        }

        payload = {
                "grant_type": "password",
                "username": pim_username,
                "password": pim_pwd
            }
        response = requests.post(pim_url + "oauth/v1/token",data=json.dumps(payload),headers=headers).json()
        try:
            return response['access_token']
        except:
            return response


    wcapi = API(
        url="https://www.meo.fr",
        consumer_key=api_client,
        consumer_secret=api_secret,
        wp_api=True,
        version="wc/v3"
    )



    first_call = wcapi.get("products?status=publish&per_page=100")
    tot = int(first_call.headers['X-WP-TotalPages']) + 1
    product = first_call.json()
    for i in range(2,tot):
        product.extend(wcapi.get(f"products?status=publish&per_page=100&page={i}").json())

    listing_google = []
    access_token = get_pim_access_token()
    for p in product:
        payload = {}
        headers={
            "Accept" : "application/json",
            "Authorization" : f"Bearer {access_token}"
        }
        url = 'https://akeneo.meo.fr/api/rest/v1/products?search={"identifier":[{"operator":"=","value":"'+ p['sku'] + '","scope":"meo_fr"}]}'
        try:
            akeneo_data = requests.get(url,data=json.dumps(payload),headers=headers).json()['_embedded']['items'][0]
        except:
            print(p['sku'])

        try:
            ean = akeneo_data['values']['ean'][0]['data']
        except:
            ean = ''

        try:
            brand =  akeneo_data['values']['marque'][0]['data']
        except:
            brand = ''

        try:
            new_prod = {
                'offerId':
                    p['sku'],
                'title':
                    p['name'],
                'description':
                    p['short_description'],
                'link':
                    p['permalink'],
                'imageLink':
                    p['images'][0]['src'],
                'contentLanguage':
                    'fr',
                'targetCountry':
                    'FR',
                'channel':
                    'online',
                'availability':
                    'in stock',
                'condition':
                    'new',
                'gtin':
                    ean,
                'price': {
                    'value': p['regular_price'],
                    'currency': 'EUR'
                },
                'brand': brand
                #'shipping': [{
                #    'country': 'FR',
                #    'service': 'Standard shipping',
                #    'price': {
                #        'value': '0.99',
                #        'currency': 'USD'
                #    }
                #}],
                #'shippingWeight': {
                #    'value': '200',
                #    'unit': 'grams'
                #}
            }

            try:
                sales_date = p['date_on_sale_from_gmt'][:-3]+'+0000 / ' + p['date_on_sale_to_gmt'][:-3]+'+0000'
                if p['sale_price']=='':
                    sales_price = ''
                    sales_date = ''
                else:
                    sales_price = {
                            'value': p['sale_price'],
                            'currency': 'EUR'
                        }
            except:
                sales_date = ''
                sales_price = ''
            if sales_price != '':
                new_prod['salePriceEffectiveDate'] = sales_date
                new_prod['salePrice'] = sales_price
            listing_google.append(new_prod)
        except:
            print('error on '+p['name'])

    return listing_google


def main(argv):
  # Construct the service object to interact with the Content API.
  service, config, _ = common.init(argv, __doc__)

  # Get the merchant ID from merchant-info.json.
  merchant_id = config['merchantId']

  product = get_all_product(config['WOO_COMMERCE_API_CLIENT'],config['WOO_COMMER_API_SECRET'],config['PIM_TOKEN'],config['PIM_USERNAME'],config['PIM_PWD'],config['PIM_URL'])
  #product = [0,1]
  # Create the request with the merchant ID and product object.
  for p in product:
    #p = {'offerId': '29901', 'title': 'Boîte festive café moulu - Ethiopie Kaffa 250g', 'description': '<p style="margin-right: 0px; margin-left: 0px; padding-bottom: 0px; color: rgb(100, 103, 110); min-height: 10px; font-family: Segoe-UI; font-size: 17px;"><span id="p0">La boîte&nbsp;festive&nbsp;de l&#8217;année par&nbsp;<span id="5">Méo</span>&nbsp;!</span></p>\n<p style="margin-right: 0px; margin-left: 0px; padding-bottom: 0px; color: rgb(100, 103, 110); min-height: 10px; font-family: Segoe-UI; font-size: 17px;"></p>\n<p style="margin-right: 0px; margin-left: 0px; padding-bottom: 0px; color: rgb(100, 103, 110); min-height: 10px; font-family: Segoe-UI; font-size: 17px;"><span id="p17">Découvrez notre nouvelle gamme de café pour les fêtes de fin d&#8217;année avec cette boîte en métal hermétique et design contenant un café 100 % arabica d&#8217;Ethiopie&nbsp;<span id="p16">(région de&nbsp;<span id="18" class="s-rg-t">Kaffa</span>)</span>.</span><span id="p3">&nbsp;Une&nbsp;boîte jeune de&nbsp;250 g&nbsp;de café en moulu contenant également un&nbsp;<span id="12">leaflet</span>&nbsp;où vous pourrez découvrir la légende de&nbsp;<span id="13">Kaldi.</span></span></p>\n<p style="margin-right: 0px; margin-left: 0px; padding-bottom: 0px; color: rgb(100, 103, 110); min-height: 10px; font-family: Segoe-UI; font-size: 17px;"><span id="p3"><br /></span></p>\n<p style="margin-right: 0px; margin-left: 0px; padding-bottom: 0px; color: rgb(100, 103, 110); min-height: 10px; font-family: Segoe-UI; font-size: 17px;"><span id="p3"><span id="13"><span style="color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(248, 248, 248);">Notes gustatives : Agrumes, Floral, Fruité</span></span></span></p>\n', 'link': 'https://www.meo.fr/produit/boite-festive-cafe-moulu-ethiopie-kaffa-250g/', 'imageLink': 'https://i0.wp.com/dam.meo.fr/asset/public/preview/830x830/1108.jpg?w=830&resize=830%2C&ssl=1', 'contentLanguage': 'fr', 'targetCountry': 'FR', 'channel': 'online', 'availability': 'in stock', 'condition': 'new', 'gtin': '3261342004577', 'price': {'value': '5.95', 'currency': 'EUR'}, 'brand': 'Méo'}
    request = service.products().insert(merchantId=merchant_id, body=p)

  # Execute the request and print the result.
    try:
        result = request.execute()
        print(result)
    except:
        print('Produit non importé')
        print(p)
  #print('Product with offerId "%s" was created.' % (result['offerId']))
    

# Allow the function to be called with arguments passed from the command line.
if __name__ == '__main__':
  main(sys.argv)
