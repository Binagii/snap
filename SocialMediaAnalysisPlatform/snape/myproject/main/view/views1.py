import csv, openpyxl
import pandas as pd
from apify_client import ApifyClient
from django.http import HttpResponse
from io import TextIOWrapper
from django.contrib.auth.decorators import login_required
from neomodel import db
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Category
from django.contrib import messages
from .forms import UserAccountForm, CategoryForm, BusinessmanForm , ContentCreatorForm, DataAnalystForm , ProfileForm , VisibilitySettingsForm
from .models import UserAccount , Profile , DataItem , Testimonial
from django.http import JsonResponse
from django.conf import  settings
from .models import Person, Movie
from django.views.decorators.csrf import csrf_exempt

import os
import re
import csv
from collections import defaultdict
import instaloader
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

# Initialize Instaloader
L = instaloader.Instaloader()


def login_instagram(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            L.login(username, password)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
   
       

def load_session():
    """Load an existing session or log in manually."""
    session_file = os.path.join(settings.BASE_DIR, "instaloader_session")
    if os.path.exists(session_file):
        try:
            L.load_session_from_file(username=None, filename=session_file)
        except Exception:
            login(session_file)
    else:
        login(session_file)

def login(session_file):
    """Log in to Instagram and save the session."""
    username = os.getenv("INSTAGRAM_USERNAME", "default_username")
    password = os.getenv("INSTAGRAM_PASSWORD", "default_password")
    L.login(username, password)
    L.save_session_to_file(session_file)

def extract_hashtags(caption):
    """Extract hashtags from a caption."""
    if not caption:
        return []
    return re.findall(r"#(\w+)", caption)


def scrape_profile(request):
    if request.method == "POST":
        profile_username = request.POST.get("profile_username")
        try:
            profile = instaloader.Profile.from_username(L.context, profile_username)

            # Define the path for saving the CSV file
            csv_filename = f"/Users/smithjonson/Documents/{profile_username}_recent_posts_with_hashtags.csv"

            # Data to keep track of all unique hashtags
            hashtag_columns = defaultdict(int)

            # Collect post data
            posts_data = []
            for i, post in enumerate(profile.get_posts()):
                if i >= 10:  # Limit to the first 10 posts
                    break

                hashtags = extract_hashtags(post.caption)
                for hashtag in hashtags:
                    hashtag_columns[hashtag] = 1  # Mark the hashtag as a column

                post_details = {
                    "Post URL": f"https://www.instagram.com/p/{post.shortcode}/",
                    "Image URL": post.url,
                    "Likes": post.likes,
                    "Comments": post.comments,
                    "Caption": post.caption or "No caption",
                    "Date": post.date,
                }
                # Add hashtags as keys with binary values (1 if present, 0 otherwise)
                for hashtag in hashtag_columns.keys():
                    post_details[f"#{hashtag}"] = 1 if hashtag in hashtags else 0

                posts_data.append(post_details)

            # Prepare final fieldnames for CSV (dynamic hashtags as columns)
            base_fields = ["Post URL", "Image URL", "Likes", "Comments", "Caption", "Date"]
            hashtag_fields = [f"#{hashtag}" for hashtag in hashtag_columns.keys()]
            fieldnames = base_fields + hashtag_fields

            # Write to CSV
            with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for post_data in posts_data:
                    writer.writerow(post_data)

            # Return success with the generated file path
            return JsonResponse({"success": True, "csv_path": csv_filename ,})
            
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, "main/scraper.html")









# Sample data for testing
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'David', None],
    'age': [25, 30, 35, 40, None],
    'from_location': ['New York', 'Los Angeles', 'Chicago', 'Houston', None],
    'klout_score': [80, 75, 90, 85, None]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the data as a CSV file
df.to_csv('export.csv', index=False)

print("Sample file 'export.csv' created successfully.")


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Use Django's built-in authentication system

        try:
            user_account = UserAccount.objects.get(username=username)
            if user_account.password == password:  # This is fine if not using Django's auth
                # Set session for login
                request.session['username'] = user_account.username
                request.session['role'] = user_account.role
                request.session['is_authenticated'] = True

                # Redirect to respective dashboards based on role
                if user_account.role == 'admin':
                    return redirect('dashboard')
                elif user_account.role == 'businessman':
                    return redirect('businessman_dashboard')
                elif user_account.role == 'content_creator':
                    return redirect('content_creator_dashboard')
                elif user_account.role == 'data_analyst':
                    return redirect('data_analyst_dashboard')
            else:
                messages.error(request, "Invalid credentials!")
        except UserAccount.DoesNotExist:
            messages.error(request, "Account does not exist!")

    return render(request, 'main/login.html')











        

def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def businessman_dashboard(request):
   return render(request, 'main/businessman.html')


def content_creator_dashboard(request):
    return render(request, 'main/content_creator.html')


def data_analyst_dashboard(request):
    return render(request, 'main/data_analyst.html')


# Dashboard View
def dashboard(request):
    return render(request, 'main/dashboard.html')



# Create Category
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('category_list')
    
    else: 
        form = CategoryForm()  #Empty form for GET requet
    return render(request, 'main/create_category.html', {'form': form}) 


@csrf_exempt
def update_category(request, category_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        try:
            category = Category.objects.get(id=category_id)
            category.name = name
            category.description = description
            category.save()

            # Return both the updated name and description
            return JsonResponse({
                'status': 'success',
                'id': category.id,
                'name': category.name,
                'description': category.description
            })
        except Category.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Category not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
  
    
def category_list(request):
    categories = Category.objects.all()  # Make sure this is fetching the categories correctly
    return render(request, 'main/category_list.html', {'categories': categories})

import requests
def get_timezone_from_ip(ip):
    try: 
        #using ip-api to get timezone
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            return data.get("timezone", "Unknown")
    
    except Exception as e:
        print(f"Error fetching timezone: {e}")
    return "Unknown"        

#create profile 
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            #Save the form data to create a new profile instance
            form.save()
            #Redirect to a success page or another relevant page
            return redirect('businessman_dashboard')
    
    else :
        # Get user IP address
        ip = "124.197.66.11"
        timezone = get_timezone_from_ip(ip)
        form = ProfileForm(initial={'timezone' : timezone})
        
        
    # Render the template with the form
    return render(request, 'main/create_profile.html', {'form' : form})        
  
  
def get_client_ip(request):
    """ Extract the client's IP from the request headers"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
        
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip                
            

#create user account      
def create_user_account(request):
    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        if form.is_valid():
            
            # Check for duplicate usernames or emails
            
            if UserAccount.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Username already exists!")
            elif UserAccount.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already exists!")
            else:
                # Save the user account
                
                user_account = form.save(commit=False)  # Do not save to DB yet
                user_account.role = 'admin'
                user_account.save()
                
                messages.success(request, "User account created successfully!")
                return redirect('create_profile')  # Redirect to success page

        else:
            messages.error(request, "Failed to create account. Please check your input.")
    else:
        form = UserAccountForm()

    return render(request, 'main/create_user_account.html', {'form': form})

def create_businessman_account(request):
    if request.method == 'POST':
        form = BusinessmanForm(request.POST)
        if form.is_valid():
            # Check for duplicate usernames or emails
            if UserAccount.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Username already exists!")
            elif UserAccount.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already exists!")
            else:
                # Save the user account and set role to 'businessman'
                user_account = form.save(commit=False)  # Do not save to DB yet
                user_account.role = 'businessman'       # Assign role in backend
                user_account.save()                    # Save to DB
                messages.success(request, "Businessman account created successfully!")
                return redirect('create_businessman_account')  # Redirect back to the form
    else:
        form = BusinessmanForm()
    return render(request, 'main/create_businessman_acc.html', {'form': form})


def create_content_creator_account(request):
    if request.method == 'POST':
        form = ContentCreatorForm(request.POST)
        if form.is_valid():
            if UserAccount.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Username already exists!")
            elif UserAccount.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already exists!")
            else: 
                user_account = form.save(commit=False)
                user_account.role = 'content_creator'
                user_account.save()
                
                messages.success(request, "Content cretor account created successfully!")
                return redirect('create_content_creator_account')
    else :
        form = ContentCreatorForm()
    return render(request, 'main/create_content_creator_acc.html', {'form': form}) 

def create_data_analyst_account(request):
    if request.method == 'POST':
        form = DataAnalystForm(request.POST)
        if form.is_valid():
            if UserAccount.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Username already exists!")
            elif UserAccount.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already exists!")
            else :
                user_account = form.save(commit=False)
                user_account.role = 'data_analyst'
                user_account.save()
                messages.success(request, "Data analyst account created successfully!")
                return redirect('create_data_analyst_account')
    else :
        form = DataAnalystForm()
    return render(request, 'main/create_data_analyst_acc.html', {'form': form})                    
                           
#view user profile
def view_profile(request):
    user_profile  = Profile.objects.all()
    return render(request, 'main/myprofile.html', {'user_profile' : user_profile})
#View to list all user accounts
def view_user_accounts(request):
    users = UserAccount.objects.all()
    return render(request, 'main/view_user_accounts.html', {'users': users})

def view_businessman_accounts(request):
    users = UserAccount.objects.filter(role  = 'businessman')
    return render(request, 'main/view_businessman_accounts.html', {'users': users})

def view_content_creator_accounts(request):
    users = UserAccount.objects.filter(role = 'content_creator')
    return render(request, 'main/view_content_accounts.html', {'users': users})

def view_data_analyst_accounts(request):
    users = UserAccount.objects.filter(role = 'data_analyst')
    return render(request, 'main/view_data_analyst_accounts.html', {'users':users})



def update_user_account(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(UserAccount, id=user_id)
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'})


import json

def update_profile(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, profile_id=profile_id)
        data = json.loads(request.body) # Parse JSON data
        profile.first_name = data.get('first_name' , profile.first_name)
        profile.last_name = data.get('last_name' , profile.last_name)
        profile.company = data.get('company' , profile.company)
        profile.timezone = data.get('timezone' , profile.timezone)
        
        profile.save()
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'}, status=400)


import os
from dotenv import load_dotenv


# Extract Data
            





from django.http import HttpResponse
import csv



#upload csv

import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages


import os
import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages


def upload_csv_or_xlsx(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "Error: No file uploaded.")
            return redirect('upload_csv_or_xlsx')

        try:
            # Save the original file name in the session
            original_file_name = os.path.splitext(uploaded_file.name)[0]
            cleaned_file_name = original_file_name.strip() + ".csv"
            request.session['original_file_name'] = cleaned_file_name

            # Read CSV file
            file_data = TextIOWrapper(uploaded_file.file, encoding='utf-8')
            df = pd.read_csv(file_data)

            # Clean and convert numeric columns
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric where possible
            
            # Replace NaNs with a placeholder or drop them
            df = df.dropna(axis=0, how='all')  # Drop rows where all values are NaN

            # Extract headers and data for later use
            headers = df.columns.tolist()
            data = df.to_dict(orient='records')  # Convert cleaned DataFrame to a list of dictionaries

            if not headers:
                messages.error(request, "The CSV file must have at least one column.")
                return redirect('upload_csv_or_xlsx')

            # Save headers and data to session
            request.session['uploaded_headers'] = headers
            request.session['uploaded_data'] = data
            messages.success(request, f"File {cleaned_file_name} uploaded successfully.")
            return redirect('auto_preprocess')
            
            

        except Exception as e:
            messages.error(request, f"Error processing the file: {str(e)}")
            return redirect('upload_csv_or_xlsx')

    return render(request, "main/upload_excel.html")


import pandas as pd
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages





#auto_data process

import pandas as pd

#use


def auto_preprocess(request):
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    from sklearn.impute import SimpleImputer

    if request.method == 'POST':
        try:
            # Retrieve uploaded data from the session
            uploaded_data = request.session.get('uploaded_data', [])
            if not uploaded_data:
                messages.error(request, "No data available for preprocessing. Please upload a file first.")
                return redirect('upload_csv_or_xlsx')

            # Convert session data to DataFrame
            df = pd.DataFrame(uploaded_data)
            print("Original DataFrame:")
            print(df.head())  # Print original data for verification

            # Step 1: Drop rows and columns where all values are NaN
            df.dropna(how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
            print("After Dropping Empty Rows/Columns:")
            print(df.head())  # Verify after removing empty rows/columns

            # Step 2: Clean column names dynamically
            df.columns = (
                df.columns.str.strip()
                .str.replace(r'\W+', '_', regex=True)
                .str.lower()
            )
            print("Cleaned Column Names:")
            print(df.columns)  # Verify cleaned column names

            # Remove columns with a single unique value (constant columns)
            df = df.loc[:, df.nunique() > 1]
            print("After Removing Constant Columns:")
            print(df.head())  # Verify columns with unique values removed

            # Remove columns with > 90% missing values
            df = df.loc[:, df.isnull().mean() < 0.9]
            print("After Dropping Columns with >90% Missing Values:")
            print(df.head())  # Verify after dropping columns with high missing data

            # Step 3: Process columns dynamically
            label_encoder = LabelEncoder()
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().replace({'nan': '', 'NaN': '', 'None': ''})
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if df[col].isnull().all():
                        df[col] = label_encoder.fit_transform(df[col].astype(str))
                elif pd.api.types.is_numeric_dtype(df[col]):
                    df[col].fillna(0, inplace=True)

            print("Processed DataFrame:")
            print(df.head())  # Verify processed data

            # Step 4: Sample rows for performance
            if len(df) > 500:
                df = df.sample(n=500, random_state=42)
                print("Sampled DataFrame:")
                print(df.head())  # Verify sampling

            # Save cleaned data back to the session
            request.session['uploaded_data'] = df.to_dict(orient='records')
            request.session['uploaded_headers'] = df.columns.tolist()

            messages.success(request, "Data successfully preprocessed. All columns converted to numeric where possible.")
            return redirect('manual_preprocess')

        except Exception as e:
            messages.error(request, f"Error during preprocessing: {str(e)}")
            return redirect('upload_csv_or_xlsx')

    return render(request, 'main/data_management.html')





#auto_data process






            

from sklearn.preprocessing import LabelEncoder











def manual_preprocess(request):
    import math

    # Pagination settings
    PAGE_SIZE = 100  # Number of rows per page
    if request.method == 'POST':
        try:
            # Retrieve uploaded data from the session
            uploaded_data = request.session.get('uploaded_data', [])
            headers = request.session.get('uploaded_headers', [])

            # Update rows with submitted data
            for index, row in enumerate(uploaded_data):
                for header in headers:
                    field_name = f'data_{index}_{header}'
                    row[header] = request.POST.get(field_name, row.get(header, ''))

            # Save updated data back to the session
            request.session['uploaded_data'] = uploaded_data
            messages.success(request, "Data successfully updated.")
            return redirect('create_or_view_visualization')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('manual_preprocess')

    # Retrieve data for display
    uploaded_data = request.session.get('uploaded_data', [])
    headers = request.session.get('uploaded_headers', [])
    
    # Implement pagination
    page = int(request.GET.get('page', 1))
    total_pages = math.ceil(len(uploaded_data) / PAGE_SIZE)
    paginated_data = uploaded_data[(page -1) * PAGE_SIZE : page * PAGE_SIZE]

    return render(request, 'main/manual.html', {'data': paginated_data, 
                                                'headers': headers,
                                                'current_page': page,
                                                'total_pages': total_pages})

  
        
# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


def dashboard_view(request):
    # Retrieve headers and data from session
    headers = request.session.get('uploaded_headers', [])
    uploaded_data = request.session.get('uploaded_data', [])

    if not headers or not uploaded_data:
        messages.error(request, "No data uploaded. Please upload a file first.")
        return redirect('upload_csv_or_xlsx')

    # Filter numeric columns only
    df = pd.DataFrame(uploaded_data)
    numeric_headers = [col for col in headers if pd.api.types.is_numeric_dtype(pd.to_numeric(df[col], errors='coerce'))]

    return render(request, 'main/dash_visualization.html', {
        'headers': numeric_headers
    })








#use



import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from django.shortcuts import render, redirect
from django.contrib import messages
import io
import base64




def create_or_view_visualization(request):
    try:
        # Retrieve uploaded data
        uploaded_data = request.session.get('uploaded_data', [])
        headers = request.session.get('uploaded_headers', [])

        if not uploaded_data or not headers:
            messages.error(request, "No data available for visualization.")
            return redirect('upload_csv_or_xlsx')

        # Step 1: Build the Graph
        G = nx.Graph()
        for row in uploaded_data:
            row_nodes = []
            for header in headers:
                value = row.get(header)
                if value and isinstance(value, str) and len(value) < 50 and value not in ['null', 'None', 'nan', '-', '']:
                    if 'http' in value or 'timestamp' in header.lower():
                        continue
                    G.add_node(value)
                    row_nodes.append(value)

            # Add edges with dynamic limit
            max_edges_per_node = 10
            node_edges_count = {}
            for i in range(len(row_nodes)):
                for j in range(i + 1, len(row_nodes)):
                    node1, node2 = row_nodes[i], row_nodes[j]
                    if node_edges_count.get(node1, 0) >= max_edges_per_node:
                        continue
                    if node_edges_count.get(node2, 0) >= max_edges_per_node:
                        continue
                    G.add_edge(node1, node2)
                    node_edges_count[node1] = node_edges_count.get(node1, 0) + 1
                    node_edges_count[node2] = node_edges_count.get(node2, 0) + 1

        # Step 2: Calculate Centrality Metrics
        degree_centrality = nx.degree_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)

        # Combine centrality measures into a dictionary
        centrality_metrics = {}
        for node in G.nodes():
            centrality_metrics[node] = {
                "degree": degree_centrality.get(node, 0),
                "closeness": closeness_centrality.get(node, 0),
                "betweenness": betweenness_centrality.get(node, 0)
            }

        # Identify top nodes by degree centrality
        top_degree_nodes = sorted(degree_centrality, key=degree_centrality.get, reverse=True)[:10]

        # Step 3: Dynamic Layout
        layout_style = request.GET.get('layout', 'kamada_kawai')
        if layout_style == 'spring':
            pos = nx.spring_layout(G, k=0.5, seed=42)  # Adjust "k" for spacing
        elif layout_style == 'circular':
            pos = nx.circular_layout(G)
        else:
            pos = nx.kamada_kawai_layout(G)  # Kamada-Kawai for better large graph visualization



        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}<br>Degree: {degree_centrality[node]:.2f}")

        # Edge trace for plotly
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Node trace for plotly
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            marker=dict(
                size=[degree_centrality[node] * 20 + 10 for node in G.nodes()],
                color=['orange' if node in top_degree_nodes else 'skyblue' for node in G.nodes()],
                line_width=2
            ),
            hoverinfo='text'
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Interactive Network Visualization',
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))
        
        # Prepare centrality results for frontend display
        centrality_results = [
            {"node": node, "degree": round(metrics["degree"], 4), 
             "closeness": round(metrics["closeness"], 4), 
             "betweenness": round(metrics["betweenness"], 4)}
            for node, metrics in sorted(centrality_metrics.items(), key=lambda x: x[1]["degree"], reverse=True)[:10]
        ]

        # Convert to HTML
        graph_html = fig.to_html(full_html=False)
        
        # Determine the template
        template = 'main/businessman.html' if request.GET.get('view') == 'businessman' else 'main/view_visualization.html'


        # Render visualization
        return render(request, template, {
            'graph_html': graph_html,
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'headers': headers,
            'centrality_results': centrality_results  # Top nodes with centrality scores
        })

    except Exception as e:
        messages.error(request, f"Error creating visualization: {str(e)}")
        return redirect('upload_csv_or_xlsx')





import plotly.graph_objects as go


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

def test_predictive_models(request):
    try:
        # Retrieve uploaded data
        uploaded_data = request.session.get('uploaded_data', [])
        headers = request.session.get('uploaded_headers', [])

        if not uploaded_data or not headers:
            messages.error(request, "No data available for model testing. Please upload data.")
            return redirect('upload_csv_or_xlsx')

        # Load data into DataFrame
        df = pd.DataFrame(uploaded_data)
        print("Original DataFrame:")
        print(df.dtypes)
        print(df.head())
        
        

        # User inputs from form
        target_column = request.GET.get('target_column')
        model_type = request.GET.get('model_type', 'linear_regression')

        # Input validation: Target column exists
        if not target_column or target_column not in df.columns:
            messages.error(request, "Please select a valid target column.")
            return redirect('create_or_view_visualization')
        
        # Step 1: Convert target column to numeric
        df[target_column] = pd.to_numeric(df[target_column], errors='coerce')
        if df[target_column].isnull().all():
            messages.error(request, f"Target column '{target_column}' is not numeric and cannot be converted.")
            return redirect('create_or_view_visualization')

        # Step 2: Handle non-numeric features (encode them)
        numeric_df = df.copy()
        label_encoder = LabelEncoder()

        for col in numeric_df.columns:
            if col != target_column and numeric_df[col].dtype == 'object':
                print(f"Encoding column: {col}")
                numeric_df[col] = numeric_df[col].fillna('Missing')  # Replace NaNs with a placeholder
                numeric_df[col] = label_encoder.fit_transform(numeric_df[col].astype(str))
            numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')  # Ensure numeric conversion

        # Drop rows with missing target values
        numeric_df = numeric_df.dropna(subset=[target_column])

        # Define features and target
        X = numeric_df.drop(columns=[target_column])
        y = numeric_df[target_column]
        
        

        # Check if there are valid features left
        if X.empty or y.empty:
            messages.error(request, "No valid features left for modeling after preprocessing.")
            return redirect('create_or_view_visualization')

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Run selected model
        metrics = {}
        if model_type == 'linear_regression':
            model = LinearRegression()
        elif model_type == 'decision_tree':
            model = DecisionTreeRegressor()
        elif model_type == 'random_forest':
            model = RandomForestRegressor()   
        else:
            messages.error(request, "Invalid model type selected.")
            return redirect('create_or_view_visualization')

        # Train and predict
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        # Calculate metrics
        metrics = {
            "Mean Squared Error": mean_squared_error(y_test, predictions),
            "R2 Score": r2_score(y_test, predictions)
        }

        # Plot the predictions
        buf = io.BytesIO()
        plt.figure(figsize=(10, 6))
        plt.plot(y_test.values[:50], label="Actual", marker='o')
        plt.plot(predictions[:50], label="Predicted", marker='x')
        plt.legend()
        plt.title(f"{model_type.replace('_', ' ').title()} - Predicted vs Actual")
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Render the predictive model results
        return render(request, 'main/predictive.html', {
            'metrics': metrics,
            'prediction_plot': f"data:image/png;base64,{img_base64}",
            'model_type': model_type
        })

    except Exception as e:
        messages.error(request, f"Model testing failed: {str(e)}")
        return redirect('create_or_view_visualization')










from neo4j import GraphDatabase

    
def save_to_neo4j(graph, headers):

    import logging
    #Neo4j connection details
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "bin754826" 
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    



    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def add_to_neo4j(tx, node1,node2):
        query = """
        MERGE (n1:Node {name: $node1})
        MERGE (n2:Node {name: $node2})
        MERGE (n1)-[r:RELATION]->(n2)
        """
        
        tx.run(query, node1=node1, node2=node2)
        
    with driver.session() as session:
        for edge in graph.edges:
            session.write_transaction(add_to_neo4j, edge[0], edge[1])
            
    driver.close()   
    logger.info("All data saved to Neo4j successfully.")  
                                        
#----------------------------GRAPH VISUALIZATION----------------------------


#download csv
def download_csv(request):
    # Retrieve uploaded data and original file name from the session
    uploaded_data = request.session.get('uploaded_data', None)
    headers = request.session.get('uploaded_headers', None)
    original_file_name = request.session.get('original_file_name', "uploaded_data.csv")  # Default if no name is found
    
    if not uploaded_data or not headers:
        messages.error(request, "No uploaded data available for download. Please upload a file first.")
        return redirect('upload_csv_or_xlsx')
    
    # Ensure the file has a .csv extension
    if not original_file_name.endswith('.csv'):
        original_file_name += '.csv'

    # Create the HTTP response with the correct content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{original_file_name}"'

    
    # Write uploaded data to CSV
    writer = csv.DictWriter(response, fieldnames=headers)
    writer.writeheader()
    writer.writerows(uploaded_data)

    return response



#-------------------------------------------------------




def  marketing_page(request):
    testimonials = Testimonial.objects.all().order_by("-created_at")
    return render(request, 'main/marketing_page.html' , {'testimonials' : testimonials})
'''
if username:
            user_account = UserAccount.objects.get(username=username)
            Testimonial.objects.create(user=user_account, content=content, rating=rating)
            return redirect('marketing_page')  # Redirect back to marketing page

    return render(request, "main/testimonial_page.html")
'''

def testimonial_page(request):
    if request.method == "POST":
        rating = request.POST.get("rating")
        content = request.POST.get("content")
        username = request.session.get("username")
        
        if username:
            user_account = UserAccount.objects.get(username=username)
            Testimonial.objects.create(user=user_account, content=content, rating=rating)
            return redirect('marketing_page')
    
    return render(request, 'main/testimonial_page.html')    
        
        
        


def login_rate(request):
    return render(request, 'main/rate_to_login.html')


#-------------------------------------------------------


def manage_visibility(request):
    is_authenticated = request.session.get('is_authenticated', False)

    if not is_authenticated:
        return redirect('admin_login')

    username = request.session.get('username')
    user_account = UserAccount.objects.get(username=username)

    # Query DataItem using UserAccount
    data_items = DataItem.objects.filter(businessman=user_account)
    
    print(f"User Account: {user_account}")
    print(f"Data Items: {data_items}")

    return render(request, 'main/manage_visibility.html', {'data_items': data_items})

def update_visibility(request, data_item_id):
    username = request.session.get('username')
    user_account = UserAccount.objects.get(username=username)

    data_item = get_object_or_404(DataItem, id=data_item_id, businessman=user_account)
    
    if request.method == 'POST':
        form = VisibilitySettingsForm(request.POST, instance=data_item)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Visibility settings updated successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to update visibility settings. Please retry.'})
    
    form = VisibilitySettingsForm(instance=data_item)
    return render(request, 'main/update_visibility.html', {'form': form, 'data_item': data_item})



