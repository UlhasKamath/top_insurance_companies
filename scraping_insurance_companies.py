#import required modules
import requests
import pandas as pd
from bs4 import BeautifulSoup

#function to get url from a page
def get_url(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Response code: ", response.status_code)
        raise Exception(f'Cannot download {url}')
        
    doc = BeautifulSoup(response.text, 'html.parser')
    return doc

insurance_doc = get_url('https://www.value.today/world-top-companies/insurance')

# Extracting li tags that contain all the information about the company
companies_data = insurance_doc.find_all('li', {'class':'row well clearfix'})

# Function to extract company name
def get_company_name(companies_data):
    company_names = []

    for tag in companies_data:
        name = tag.find('div', class_='field field--name-node-title field--type-ds field--label-hidden field--item').find('a').text
        company_names.append(name)
    
    return company_names  

# Function to extract company's CEO's name
def get_company_ceo(companies_data):
    company_ceos = []
    
    for tag in companies_data:
        names = tag.find('div', class_='clearfix col-sm-12 field field--name-field-ceo field--type-entity-reference field--label-above')
        try:
            ceo = names.find('a').text
            company_ceos.append(ceo)
        except AttributeError:
            company_ceos.append(None)
    
    return company_ceos

# Function to extract world ranking of the company
def get_world_rank(companies_data):
    world_ranks = []
    
    for tag in companies_data:
        rank = tag.find('div', class_='clearfix col-sm-6 field field--name-field-world-rank-jan072022 field--type-integer field--label-above')
        w_rank = rank.find('div', class_='field--item').text
        world_ranks.append(w_rank)
        
    return world_ranks

# Function to extract company's stock type
def get_stock_type(companies_data):
    stock_data = []
    
    for tag in companies_data:
        stock_tag = tag.find('div', class_='clearfix col-sm-12 field field--name-field-stock-category-lc field--type-entity-reference field--label-inline')
        
        try:
            stock = stock_tag.find('div', class_='field--item').find('a').text
            stock_data.append(stock)
        except AttributeError:
            stock_data.append(None)
            
    return stock_data

# Function to extract company's annual revenue
def get_annual_revenue(companies_data):
    annual_revenue = []
    
    for tag in companies_data:
        rev = tag.find('div', class_='clearfix col-sm-12 field field--name-field-revenue-in-usd field--type-float field--label-inline')
        try:
            revenue = rev.find('div', class_='field--item').text.replace(' Million USD', '').replace(',', '')
            annual_revenue.append(int(revenue))
        except AttributeError:
            annual_revenue.append(None)

    return annual_revenue

# Function to extract number of employees in the company
def get_no_of_employees(companies_data):
    num_employees = []
    
    for tag in companies_data:
        emp = tag.find('div', class_='clearfix col-sm-12 field field--name-field-employee-count field--type-integer field--label-inline')
        try:
            no_emp = emp.find('div', class_='field--item').text.replace(',', '')
            num_employees.append(int(no_emp))
        except AttributeError:
            num_employees.append(None)

    return num_employees

# Function to extract url of the company's website
def get_company_urls(companies_data):
    company_urls = []
    
    for tag in companies_data:
        url_tag = tag.find('div', class_='clearfix col-sm-12 field field--name-field-company-website field--type-link field--label-above')
        try:
            url = url_tag.find('div', class_='field--item').find('a')['href']
            company_urls.append(url)
        except AttributeError:
            company_urls.append(None)

    return company_urls

# Function to extract information from all the pages   

def scrape_insurance_pages():
    companies_dict = {}
    
    companies_dict = {
        'Company Name' : [],
        'CEO' : [],
        'World Rank' : [],
        'Stock Type' : [],
        'Annual Revenue (In Million USD)': [],
        'Number of Employees': [],
        'Website' : []
    }
    #There are 53 pages in the insurance website, go through each of them
    for page in range(0, 53):
        
        url = f'https://www.value.today/world-top-companies/insurance?title=&field_headquarters_of_company_target_id&field_company_category_primary_target_id&field_company_website_uri=&field_market_value_jan072022_value=&page={page}'
        companies_data = get_url(url).find_all('li', class_='row well clearfix')
        
        companies_dict['Company Name'] += get_company_name(companies_data)
        companies_dict['CEO'] += get_company_ceo(companies_data)
        companies_dict['World Rank'] += get_world_rank(companies_data)
        companies_dict['Stock Type'] += get_stock_type(companies_data)
        companies_dict['Annual Revenue (In Million USD)'] += get_annual_revenue(companies_data)
        companies_dict['Number of Employees'] += get_no_of_employees(companies_data)
        companies_dict['Website'] += get_company_urls(companies_data)

        #move to next page
        page+=1
    
    return companies_dict

#Create dataframe and call the scrape function
company_df = pd.DataFrame(scrape_insurance_pages())

#Create csv file to store compiled data
company_df.to_csv('Top Insurance Companies.csv', index=None)
