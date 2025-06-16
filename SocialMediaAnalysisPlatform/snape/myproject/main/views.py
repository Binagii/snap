import calendar
import csv, openpyxl
import pandas as pd
from django.http import HttpResponse, HttpResponseBadRequest
from io import BytesIO, TextIOWrapper
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.conf import settings


from .models import Category
from django.contrib import messages
from .forms import UserAccountForm, CategoryForm, BusinessmanForm , ContentCreatorForm, DataAnalystForm , ProfileForm , VisibilitySettingsForm, CreatorForm
from .models import UserAccount , Profile , DataItem , Testimonial 
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import os
import re
import csv
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
        num_posts = int(request.POST.get("num_posts", 10))  # Default to 10 posts if no input is given

        if not profile_username:
            messages.error(request, "Profile username is required.")
            return redirect('scrape_profile')

        try:
            # Authenticate if necessary
            if not L.context.is_logged_in:
                L.login("your_instagram_username", "your_password")

            # Load profile using Instaloader
            profile = instaloader.Profile.from_username(L.context, profile_username)

            # Define a dynamic path for saving the CSV file
            csv_folder = os.path.join(settings.MEDIA_ROOT, "downloads")
            os.makedirs(csv_folder, exist_ok=True)  # Create the downloads folder if it doesn't exist
            csv_filename = os.path.join(csv_folder, f"{profile_username}_posts.csv")

            # Collect post data
            posts_data = []
            for i, post in enumerate(profile.get_posts()):
                if i >= num_posts: 
                    break

                try:
                    # Extract specific attributes, location cannot be extracted unfortunately
                    post_details = {
                        "owner_username": post.owner_username,
                        "is_verified": "YES" if profile.is_verified else "NO",
                        "followers": profile.followers,
                        "shortcode": post.shortcode,
                        "timestamp": post.date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                        "title": post.title,                       
                        "caption": post.caption,
                        "likes": post.likes,
                        "comments": post.comments,
                        "hashtags": post.caption_hashtags,  # List of hashtags
                        "is_video": post.is_video,
                        "video_url": post.video_url if post.is_video else None,
                        "video_duration": post.video_duration,
                        "image_url": post.url if not post.is_video else None,
                        "is_sponsored": post.is_sponsored,
                    }

                    posts_data.append(post_details)
                except Exception as e:
                    messages.error(request, f"Error processing post: {str(e)}")
                    return redirect('scrape_profile')

            # Prepare fieldnames for the selected attributes
            fieldnames = [
                "owner_username",
                "is_verified",
                "followers",
                "shortcode",
                "timestamp",
                "title",
                "caption",
                "likes",
                "comments",
                "hashtags",
                "is_video",
                "video_url",
                "video_duration",
                "image_url",
                "is_sponsored"
            ]

            # Write to CSV
            with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(posts_data)

            # Return success response with file URL
            file_url = os.path.join(settings.MEDIA_URL, "downloads", f"{profile_username}_posts.csv")
            messages.success(request, f"Profile scraped successfully. Download CSV: {file_url}")
            return redirect('scrape_profile')

        except Exception as e:
            messages.error(request, f"Error scraping profile: {str(e)}")
            return redirect('scrape_profile')

    return render(request, "main/scraper.html")


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        

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
            


        
# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns


def upload_and_view_charts(request):
    fig_html_list = []
    if request.method == 'POST' and 'csv_file' in request.FILES:
        try:
            csv_file = request.FILES['csv_file']
            platform = request.POST.get('platform')
            sponsored = request.POST.get('sponsored')
            post_type = request.POST.get('post_type')
            time_duration = request.POST.get('time_duration')
            df = pd.read_csv(csv_file)

            platform_handlers = {
                'instagram': handle_instagram_data
            }

            handler = platform_handlers.get(platform)
            if handler:
                fig_html_list = handler(df, sponsored, post_type, time_duration)
            else:
                fig_html_list = [f"<div>Error: Unknown platform '{platform}'</div>"]
        except Exception as e:
            fig_html_list = [f"<div>Error processing the file: {str(e)}</div>"]

    return render(request, 'main/upload_and_view_charts.html', {'fig_html_list': fig_html_list})

def handle_instagram_data(csv_raw, sponsored, post_type, time_duration):
    fig_html_list = []

    # Clean the 'Likes' column by converting to numeric
    csv_raw['Likes'] = pd.to_numeric(csv_raw['Likes'], errors='coerce')

    # Handle missing values in 'Hour'
    csv_raw = csv_raw.dropna(subset=['Hour'])

    # Convert numeric month to month name
    csv_raw['Month'] = csv_raw['Month'].apply(lambda x: calendar.month_name[int(x)])

    # Filter data based on selections
    if sponsored != 'all':
        csv_raw = csv_raw[csv_raw['Sponsored'] == (sponsored == 'yes')]
    if post_type != 'all':
        csv_raw = csv_raw[csv_raw['Is Video'] == (post_type == 'video')]

    # Define time categories and ordering
    order_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    order_months = list(calendar.month_name)[1:]  # Skip the empty string at index 0
    time_categories = {
        "month": ("Month", 'Month', order_months),
        "day_of_week": ("Day of the Week", 'Day of Upload', order_days),
        "hour": ("Hour of the Day", 'Hour', None)
    }

    time_name, time_col, time_order = time_categories[time_duration]

    # Define color palettes
    color_palettes = [
        'Set1', 'Set2', 'viridis', 'coolwarm', 'pastel',
        'deep', 'muted', 'dark', 'colorblind', 'cubehelix'
    ]
    
    # Generate plots for the selected category and time category
    palette_idx = 0
    palette = sns.color_palette(color_palettes[palette_idx % len(color_palettes)])
    palette_idx += 1

    # Ensure the time column is correctly ordered if necessary
    if time_order:
        csv_raw.loc[:, time_col] = pd.Categorical(csv_raw[time_col], categories=time_order, ordered=True)

    # Create count plot for the selected category and time feature
    count_title = f'Number of Posts by {time_name}'
    count_xlabel = time_name
    count_ylabel = 'Number of Posts'
    count_plot_html = create_countplot(csv_raw, time_col, count_title, count_xlabel, count_ylabel, order=time_order, palette=palette)
    fig_html_list.append(count_plot_html)

    # Create engagement plot (likes vs comments) for the selected category and time feature
    grouped_data = csv_raw.groupby(time_col, observed=True)[['Likes', 'Comments']].mean().reset_index()
    engagement_title = f'Average Engagement by {time_name}'
    engagement_xlabel = time_name
    engagement_ylabel = 'Average Engagement'
    engagement_plot_html = create_engagement_plot(grouped_data, time_col, engagement_title, engagement_xlabel, engagement_ylabel)
    fig_html_list.append(engagement_plot_html)

    return fig_html_list

def create_engagement_plot(data, x, title, xlabel, ylabel, ax=None):
    """
    Creates a line plot comparing likes and comments over time for engagement analysis.
    """
    fig, ax = plt.subplots(figsize=(12, 6)) if ax is None else (fig, ax)
    sns.lineplot(x=x, y='Likes', data=data, label='Likes', marker='o', ax=ax)
    sns.lineplot(x=x, y='Comments', data=data, label='Comments', marker='o', ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid()
    plot_html = plot_to_html(fig)
    plt.close(fig)
    return plot_html

def create_countplot(data, time_col, title, xlabel, ylabel, order=None, palette="Set1"):
    """
    Creates a count plot for a given time column and returns the plot as HTML.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(x=time_col, data=data, ax=ax, order=order, palette=palette)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45)
    plot_html = plot_to_html(fig)
    plt.close(fig)
    return plot_html

def plot_to_html(fig):
    """
    Convert a Matplotlib figure to an HTML img tag with responsive styling.
    """
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)  # Adjust dpi for better resolution
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    return f"<img src='data:image/png;base64,{img_str}' style='max-width: 100%; height: auto;'/>"

import matplotlib.pyplot as plt

def handle_linkedin_data(df):
    fig_html_list = []

    # Chart 1: Company distribution (Bar Chart)
    if 'Company_Name' in df.columns:
        company_counts = df['Company_Name'].value_counts().reset_index()  # 重置索引
    company_counts.columns = ['Company Name', 'Count']  # 重命名列
    fig1 = px.bar(
        company_counts,
        x='Company Name',  # 使用正确的列名
        y='Count',
        title='Company Distribution',
        labels={'Company Name': 'Company Name', 'Count': 'Count'}
    )
    fig_html_list.append(fig1.to_html(full_html=False))

    # Chart 2: Class distribution (Bar Chart)
    if 'Class' in df.columns:
        class_counts = df['Class'].value_counts().reset_index()
        class_counts.columns = ['Class', 'Count']
        fig2 = px.bar(
            class_counts,
            x='Class',
            y='Count',
            title='Class Distribution',
            labels={'Class': 'Class', 'Count': 'Count'}
        )
        fig_html_list.append(fig2.to_html(full_html=False))

    # Chart 3: Job distribution by location (Pie Chart)
    if 'Location' in df.columns:
        location_counts = df['Location'].value_counts().reset_index()
        location_counts.columns = ['Location', 'Count']
        fig3 = px.pie(
            location_counts,
            names='Location',
            values='Count',
            title='Job Distribution by Location',
        )
        fig_html_list.append(fig3.to_html(full_html=False))

    # Chart 4: Skill demand distribution (Bar Chart)
    skill_columns = [
        'PYTHON', 'C++', 'JAVA', 'HADOOP', 'SCALA', 'FLASK', 'PANDAS',
        'SPARK', 'NUMPY', 'PHP', 'SQL', 'MYSQL', 'CSS', 'MONGODB', 'NLTK',
        'TENSORFLOW', 'LINUX', 'RUBY', 'JAVASCRIPT', 'DJANGO', 'REACT',
        'REACTJS', 'AI', 'UI', 'TABLEAU', 'NODEJS', 'EXCEL', 'POWER BI',
        'SELENIUM', 'HTML', 'ML'
    ]
    if set(skill_columns).intersection(df.columns):
        skill_counts = {skill: df[skill].sum() for skill in skill_columns if skill in df.columns}
        fig4 = px.bar(
            x=list(skill_counts.keys()),
            y=list(skill_counts.values()),
            title='Skill Demand Distribution',
            labels={'x': 'Skill', 'y': 'Demand Count'}
        )
        fig_html_list.append(fig4.to_html(full_html=False))

    # Chart 5: Followers count distribution by company (Bar Chart)
    if 'LinkedIn_Followers' in df.columns and 'Company_Name' in df.columns:
        followers_by_company = df.groupby('Company_Name')['LinkedIn_Followers'].sum().reset_index()
        fig5 = px.bar(
            followers_by_company.sort_values('LinkedIn_Followers', ascending=False),
            x='Company_Name',
            y='LinkedIn_Followers',
            title='Followers Count by Company',
            labels={'Company_Name': 'Company Name', 'LinkedIn_Followers': 'Followers Count'}
        )
        fig_html_list.append(fig5.to_html(full_html=False))

    # Chart 6: Industry distribution (Pie Chart)
    if 'Company_Name' in df.columns and 'LinkedIn_Followers' in df.columns:
        # Group by 'Company_Name' and sum up 'LinkedIn_Followers'
        followers_by_company = df.groupby('Company_Name')['LinkedIn_Followers'].sum()

        # Create horizontal bar chart
        followers_by_company.sort_values(ascending=False).plot(kind='barh', figsize=(10, 6), color='skyblue')

        # Add title and labels
        plt.title('LinkedIn Followers by Company')
        plt.xlabel('LinkedIn Followers')
        plt.ylabel('Company Name')

        # Show the plot
        plt.tight_layout()
        plt.show()

    return fig_html_list










 
                                        
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
    
    return render(request, 'main/marketing_page.html' , 
                  {'testimonials' : testimonials , 
                   'range' : range(1,6)})


#use

def testimonial_page(request):
    if request.method == "POST":
        print("Form Data Received:", request.POST)  # Debug log
        rating = request.POST.get("rating", "").strip()
        content = request.POST.get("content", "").strip()
        username = request.session.get("username")
        print("Rating:", rating, "Content:", content, "Username:", username)  # Debug log

        # Validate the rating
        if not rating.isdigit() or int(rating) not in range(1, 6):
            return render(request, 'main/testimonial_page.html', {
                'error': 'Please select a valid rating between 1 and 5.'
            })

        # Save the testimonial
        if username:
            try:
                user_account = UserAccount.objects.get(username=username)
                testimonial = Testimonial.objects.create(
                    user=user_account,
                    content=content,
                    rating=int(rating)
                )
                print("Testimonial Saved:", testimonial)  # Debug log
            except UserAccount.DoesNotExist:
                print("User not found")  # Debug log
                return redirect('login_rate')  # Redirect to login if user not found
            return redirect('marketing_page')  # Redirect to marketing page
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



def home_page(request):
    return render(request, 'main/home_page.html')


#-------------------------------------------------------
#profile
#create profile
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
                role = form.cleaned_data['role']
                user_account.role = role
                user_account.save()
                
                messages.success(request, "User account created successfully!")
                
                #Redirect based on role
                if role == "businessman":
                    return redirect('create_profile')
                elif role == "content_creator":
                    return redirect('create_creator_profile')
                elif role == "data_analyst":
                    return redirect('create_analyst_profile')
                else :
                    return redirect('create_profile') # Default profile page

        else:
            messages.error(request, "Failed to create account. Please check your input.")
    else:
        form = UserAccountForm()

    return render(request, 'main/create_user_account.html', {'form': form})
        

#create profile 
def create_businessman_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.role = 'businessman'
            profile.save()
            #Redirect to a success page or another relevant page
            return redirect('businessman_dashboard')
    
    else :
        # Get user IP address
        ip = "124.197.66.11"
        timezone = get_timezone_from_ip(ip)
        form = ProfileForm(initial={'timezone' : timezone})
        
        
    # Render the template with the form
    return render(request, 'main/create_profile.html', {'form' : form})        


def create_creator_profile(request):
    if request.method == 'POST':
        form = CreatorForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.role = 'content_creator'
            print(f"Role assigned: {profile.role}")
            profile.save()
            print(f"Redirecting to content_creator_dashboard")
            return redirect('content_creator_dashboard')
    else:
        print("Loading create_profile form for content creator")
        ip = get_client_ip(request)
        timezone = get_timezone_from_ip(ip)
        form = CreatorForm(initial={'timezone': timezone})
    return render(request, 'main/create_creator_profile.html', {'form': form})


def create_analyst_profile(request):
    if request.method == 'POST':
        form = DataAnalystForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.role = 'data_analyst'
            print(f"Role assigned: {profile.role}")
            profile.save()
            print(f"Redirecting to data_analyst_dashboard")
            return redirect('data_analyst_dashboard')
    else:
        print("Loading create_profile form for data analyst")
        ip = get_client_ip(request)
        timezone = get_timezone_from_ip(ip)
        form = CreatorForm(initial={'timezone': timezone})
    return render(request, 'main/analyst_profile.html', {'form': form})



def get_client_ip(request):
    """ Extract the client's IP from the request headers"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
        
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip  

#view user profile
def view_profile_businessman(request):
    
    user_profile  = Profile.objects.filter(role='businessman')
    print(user_profile)
    return render(request, 'main/bus_profile.html', {'user_profile' : user_profile})





def view_profile_content_creator(request):
    user_profile  = Profile.objects.filter(role='content_creator')
    print(f"Content Creator Profiles : {user_profile}")
    return render(request, 'main/view_creator_profile.html', {'user_profile' : user_profile})

def view_profile_data_analyst(request):
    user_profile = Profile.objects.filter(role='data_analyst')
    print(f"Data Analyst Profiles : {user_profile}")
    return render(request, 'main/view_analyst_profile.html', {'user_profile' : user_profile})

## update news

def preds(request):
    return render(request, 'main/preds.html')


@csrf_exempt
def save_csv(request):
    if request.method == 'POST':
        csv_content = request.POST.get('csvContent')
        if csv_content:
            # Determine the next available filename
            directory = os.path.join(settings.BASE_DIR, 'media', 'downloads')
            os.makedirs(directory, exist_ok=True)
            existing_files = os.listdir(directory)
            next_number = len(existing_files) + 1
            filename = f'user{next_number}.csv'
            filepath = os.path.join(directory, filename)

            # Save the CSV content to the file
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                file.write(csv_content)

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'No CSV content provided'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from datetime import datetime

from sklearn.ensemble import GradientBoostingRegressor


# -------------------- Implementing Machine Learning for Instagram ---------------------------------
from django.views.decorators.csrf import csrf_exempt
from io import TextIOWrapper
import pandas as pd
import numpy as np
import os
from django.http import JsonResponse
from django.shortcuts import render
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV
import xgboost as xgb
import datetime

@csrf_exempt
def predict_engagement(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
        df = pd.read_csv(file_wrapper)

        # Preprocess the data
        df_encoded = pd.get_dummies(df, columns=['Day of Upload'])
        features = ['Day', 'Month', 'Year', 'Hour', 'Is Video'] + \
                  [col for col in df_encoded.columns if col.startswith('Day of Upload_')]
        X = df_encoded[features]
        y_likes = df['Likes']
        y_comments = df['Comments']
        y_log_likes = np.log1p(y_likes)
        y_log_comments = np.log1p(y_comments)
        X_train, X_test, y_log_likes_train, y_log_likes_test, y_log_comments_train, y_log_comments_test = \
            train_test_split(X, y_log_likes, y_log_comments, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        xgb_likes = xgb.XGBRegressor(random_state=42)
        xgb_comments = xgb.XGBRegressor(random_state=42)
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [3, 5],
            'learning_rate': [0.01, 0.1]
        }
        grid_search_likes = GridSearchCV(
            estimator=xgb_likes,
            param_grid=param_grid,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )
        grid_search_likes.fit(X_train_scaled, y_log_likes_train)
        xgb_comments.set_params(**grid_search_likes.best_params_)
        xgb_comments.fit(X_train_scaled, y_log_comments_train)

        likes_r2 = r2_score(y_log_likes_test, grid_search_likes.predict(X_test_scaled))
        comments_r2 = r2_score(y_log_comments_test, xgb_comments.predict(X_test_scaled))

        likes_mae = mean_absolute_error(y_log_likes_test, grid_search_likes.predict(X_test_scaled))
        comments_mae = mean_absolute_error(y_log_comments_test, xgb_comments.predict(X_test_scaled))

        likes_mse = mean_squared_error(y_log_likes_test, grid_search_likes.predict(X_test_scaled))
        comments_mse = mean_squared_error(y_log_comments_test, xgb_comments.predict(X_test_scaled))

        def get_recent_10_posts():
            return df.head(10)

        if request.method == 'POST':
            date = request.POST.get('date')
            hour = int(request.POST.get('hour'))
            post_type = request.POST.get('post_type')

            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
            day = date_obj.day
            month = date_obj.month
            year = date_obj.year
            day_of_week = date_obj.strftime('%A')

            is_video = 1 if 'Video' in post_type else 0

            input_data = {
                'Day': [day],
                'Month': [month],
                'Year': [year],
                'Hour': [hour],
                'Is Video': [is_video]
            }

            for col in df_encoded.columns:
                if col.startswith('Day of Upload_'):
                    input_data[col] = [1 if col == f'Day of Upload_{day_of_week}' else 0]

            input_df = pd.DataFrame(input_data)
            input_scaled = scaler.transform(input_df)

            likes_pred = np.expm1(grid_search_likes.predict(input_scaled)).astype(float)
            comments_pred = np.expm1(xgb_comments.predict(input_scaled)).astype(float)


            return JsonResponse({
                'likes_pred': likes_pred[0],
                'comments_pred': comments_pred[0],
                'likes_r2': likes_r2,
                'comments_r2': comments_r2,
                'likes_mae': likes_mae,
                'comments_mae': comments_mae,
                'likes_mse': likes_mse,
                'comments_mse': comments_mse,
                'results_df': pd.DataFrame({
                    'Actual Likes': np.expm1(y_log_likes_test),
                    'Predicted Likes': np.expm1(grid_search_likes.predict(X_test_scaled)),
                    'Actual Comments': np.expm1(y_log_comments_test),
                    'Predicted Comments': np.expm1(xgb_comments.predict(X_test_scaled))
                }).head().to_html(),
                'feature_importance': pd.DataFrame({
                    'feature': features,
                    'importance': grid_search_likes.best_estimator_.feature_importances_
                }).sort_values('importance', ascending=False).head().to_html(),
                'last_10_posts': get_recent_10_posts().to_html()
            })

    return render(request, 'main/ml_predictions.html', {
    'likes_r2': None,
    'comments_r2': None,
    'likes_mae': None,
    'comments_mae': None,
    'likes_mse': None,
    'comments_mse': None,
    'results_df': None,
    'feature_importance': None,
    'last_10_posts': None
})
#-------------------------------------------------------
# neo4j graph visualization
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from io import TextIOWrapper
import csv
import ast
from neo4j import GraphDatabase

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
        csv_reader = csv.reader(file_wrapper)
        header = next(csv_reader)  # Read the header
        
        # Process the CSV file as needed
        store_csv_to_neo4j(csv_reader)  # Ensure the CSV is stored in Neo4j
        return redirect('graph_view')  # Redirect to graph_view after successful upload
    return render(request, 'main/neoinsert.html')  # Render the form for GET requests

def store_csv_to_neo4j(csv_reader):
    driver = settings.NEO4J_DRIVER
    
    with driver.session() as session:
        for row in csv_reader:
            try:
                hashtags = ast.literal_eval(row[9])  # Assuming the hashtags are in the 10th column (index 9)
                if not isinstance(hashtags, list):
                    raise ValueError("Hashtags column is not a list")
            except (ValueError, SyntaxError, IndexError) as e:
                print(f"Error processing row {row}: {e}")
                hashtags = []  # Handle empty or invalid hashtags column
            
            print(f"Processed hashtags: {hashtags}")
            
            for i in range(len(hashtags)):
                for j in range(i + 1, len(hashtags)):
                    hashtag1, hashtag2 = hashtags[i], hashtags[j]
                    print(f"Creating relationship between {hashtag1} and {hashtag2}")
                    session.run(
                        "MERGE (h1:Hashtag {name: $hashtag1}) "
                        "MERGE (h2:Hashtag {name: $hashtag2}) "
                        "MERGE (h1)-[:CO_OCCURS_WITH]->(h2)",
                        hashtag1=hashtag1, hashtag2=hashtag2
                    )

def graph_view(request):
    driver = settings.NEO4J_DRIVER
    
    with driver.session() as session:
        result = session.run("MATCH p=()-[r:CO_OCCURS_WITH]->() RETURN p")
        
        nodes = []
        edges = []
        node_ids = set()
        
        for record in result:
            for node in record["p"].nodes:
                if node.id not in node_ids:
                    nodes.append({"id": node.id, "label": node["name"]})
                    node_ids.add(node.id)
            for rel in record["p"].relationships:
                edges.append({"from": rel.start_node.id, "to": rel.end_node.id})
    
    if not nodes:
        return JsonResponse({'error': 'Graph is empty. Upload data first.'}, status=400)
    
    G = nx.Graph()
    for node in nodes:
        G.add_node(node['id'])
    for edge in edges:
        G.add_edge(edge['from'], edge['to'])
    
    betweenness = nx.betweenness_centrality(G)
    degree = nx.degree_centrality(G)
    closeness = nx.closeness_centrality(G)
    try:
        eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        eigenvector = {node: 0 for node in G.nodes}
    
    for node in nodes:
        node['betweenness'] = betweenness[node['id']]
        node['eigenvector'] = eigenvector[node['id']]
        node['degree'] = degree[node['id']]
        node['closeness'] = closeness[node['id']]
    
    top_10_nodes = sorted(nodes, key=lambda x: x['betweenness'], reverse=True)[:10]
    
    context = {
        "nodes": json.dumps(nodes),
        "edges": json.dumps(edges),
        "centrality_results": top_10_nodes
    }
    
    return render(request, 'main/graph.html', context)


'''
@csrf_exempt
def save_visualization(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            with open('visualization.png', 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            return JsonResponse({'status': 'success', 'message': 'Visualization saved successfully!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No image provided.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
'''


import os
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def save_visualization(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            with open('visualization.png', 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            return JsonResponse({'status': 'success', 'message': 'Visualization saved successfully!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No image provided.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

#-----------------------------------------------------------------------------

# -------------------- Implementing Machine Learning for Linkedin. ---------------------------------
from django.views.decorators.csrf import csrf_exempt
from io import TextIOWrapper
import pandas as pd
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import RandomOverSampler
import warnings

warnings.filterwarnings("ignore")  # Ignore warning messages

# **Global Variables for Model and Encoders**
model = None
scaler = None
label_encoder_location = None
label_encoder_industry = None
all_locations = []
skill_columns = []  # Store skill column names


@csrf_exempt
def train_model(request):
    global model, scaler, label_encoder_location, label_encoder_industry, all_locations, skill_columns

    context = {'accuracy': None, 'message': '', 'error': ''}

    if request.method == 'POST' and request.FILES.get('linkedin_csv'):
        try:
            csv_file = request.FILES['linkedin_csv']
            file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
            df = pd.read_csv(file_wrapper)

            # **Data Cleaning**
            df['Location'] = df['Location'].str.strip()
            df['Industry'] = df['Industry'].str.strip()

            # **Define Skill Columns**
            skill_columns = [
                'PYTHON', 'C++', 'JAVA', 'HADOOP', 'SCALA', 'FLASK', 'PANDAS',
                'SPARK', 'NUMPY', 'PHP', 'SQL', 'MYSQL', 'CSS', 'MONGODB', 'NLTK',
                'TENSORFLOW', 'LINUX', 'RUBY', 'JAVASCRIPT', 'DJANGO', 'REACT',
                'REACTJS', 'AI', 'UI', 'TABLEAU', 'NODEJS', 'EXCEL', 'POWER BI',
                'SELENIUM', 'HTML', 'ML'
            ]

            # **Select Features and Target Variables**
            X = df[['Location', 'Industry']]
            y = df[skill_columns].fillna(0).astype(int)

            # **Label Encoding**
            label_encoder_location = LabelEncoder()
            label_encoder_industry = LabelEncoder()
            X['Location'] = label_encoder_location.fit_transform(X['Location'])
            X['Industry'] = label_encoder_industry.fit_transform(X['Industry'])

            # **Standardize Data**
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # **Data Balancing**
            y_str = y.apply(lambda row: '-'.join(row.astype(str)), axis=1)
            ros = RandomOverSampler(random_state=42)
            X_resampled, y_resampled = ros.fit_resample(X_scaled, y_str)

            # **Restore DataFrame**
            y_resampled = y_resampled.str.split('-', expand=True).astype(int)
            y_resampled.columns = skill_columns

            # **Split Training and Test Set**
            X_train, X_test, y_train, y_test = train_test_split(
                X_resampled, y_resampled, test_size=0.2, random_state=42
            )

            # **Train XGBoost**
            model = MultiOutputClassifier(
                        XGBClassifier(
                            eval_metric="logloss", 
                            random_state=42
                        )) 
            model.fit(X_train, y_train)

            # **Calculate Accuracy**
            y_pred = model.predict(X_test)
            accuracy = np.mean([accuracy_score(y_test.iloc[:, i], y_pred[:, i]) for i in range(y_test.shape[1])])

            # **Save All Location Values**
            all_locations = list(label_encoder_location.classes_)

            # **Pass Data to Template**
            context['accuracy'] = round(accuracy, 4)
            context['message'] = "Model training completed!"

            print(f"DEBUG: Model Accuracy = {context['accuracy']}")  # Debugging line

        except Exception as e:
            context['error'] = f'Data processing error: {str(e)}'
    
    return render(request, 'main/linkedin_preds.html', context)



@csrf_exempt
def predict_skills_view(request):
    global model, scaler, label_encoder_location, skill_columns, all_locations  # Ensure access to stored model components

    if request.method == 'POST':
        try:
            import difflib
            data = request.POST
            location = data.get('location', '').strip()

            if not location:
                return JsonResponse({'error': 'Please provide a Location'}, status=400)

            # **Find closest matching location**
            closest_match = difflib.get_close_matches(location, all_locations, n=1, cutoff=0.6)
            if closest_match:
                location = closest_match[0]
            else:
                return JsonResponse({'error': 'Location not found in training data'}, status=400)

            if model is None or scaler is None or label_encoder_location is None:
                return JsonResponse({'error': 'Model has not been trained yet'}, status=400)

            # **Encode Location**
            location_encoded = label_encoder_location.transform([location])[0]

            # **Create input DataFrame (Ensure it matches training format)**
            input_data = pd.DataFrame([[location_encoded, 0]], columns=['Location', 'Industry'])
            input_scaled = scaler.transform(input_data)

            # **Predict Skill Probabilities**
            predicted_probs = model.predict_proba(input_scaled)

            # **Ensure proper probability extraction**
            avg_probs = np.array([p[:, 1] if len(p.shape) > 1 else p for p in predicted_probs]).flatten()

            # **Ensure the number of predicted probabilities matches the skill columns**
            if len(avg_probs) != len(skill_columns):
                return JsonResponse({'error': 'Model output size mismatch'}, status=400)

            # **Sort by Probability in Descending Order**
            skill_prob_dict = {skill_columns[i]: avg_probs[i] for i in range(len(avg_probs))}
            sorted_skills = sorted(skill_prob_dict.items(), key=lambda x: x[1], reverse=True)

            # **Ensure Top 5 Skills are Returned**
            top_5_skills = [skill for skill, prob in sorted_skills[:5]]

            return JsonResponse({
                'location': location,
                'top_5_skills': top_5_skills
            })
        except Exception as e:
            return JsonResponse({'error': f'Prediction error: {str(e)}'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# **Get Location and Industry Options**
@csrf_exempt
def get_job_options(request):
    if request.method == 'POST' and request.FILES.get('linkedin_csv'):
        try:
            csv_file = request.FILES['linkedin_csv']
            file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
            df = pd.read_csv(file_wrapper)

            if 'Location' not in df.columns or 'Industry' not in df.columns:
                return JsonResponse({'error': 'CSV file is missing required columns'}, status=400)

            locations = sorted(df['Location'].dropna().unique().tolist())
            industries = sorted(df['Industry'].dropna().unique().tolist())

            return JsonResponse({'locations': locations, 'industries': industries})
        except Exception as e:
            return JsonResponse({'error': f'Unable to parse CSV: {str(e)}'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)
# ---------------------- End of Machine Learning LinkedIn ----------------------

# ----------------- Reserve for LinkedIn charts -----------------

from django.shortcuts import render
import pandas as pd
import plotly.express as px
import plotly.io as pio

def handle_linkedin_data(request):
    file_path = "C:/Users/Welcome/Downloads/snape/snape/myproject/final_data.csv"  # Update with actual path
    df = pd.read_csv(file_path)

    # Get unique locations for the dropdown filter
    locations = df["Location"].unique().tolist()

    # Apply filtering if a location is selected, but only for fig1 to fig5
    selected_location = request.GET.get("location")
    filtered_df = df if not selected_location else df[df["Location"] == selected_location]

    # Top 10 Companies by LinkedIn Followers (Filtered)
    top_companies = filtered_df.groupby("Company_Name")["LinkedIn_Followers"].max().nlargest(10).reset_index()
    fig1 = px.bar(top_companies, x='Company_Name', y='LinkedIn_Followers', title="Top 10 Companies by LinkedIn Followers", color='LinkedIn_Followers')
    
    # Pie Chart for Job Levels (Filtered)
    job_levels = filtered_df["Level"].value_counts().reset_index()
    job_levels.columns = ["Job Level", "Count"]
    fig2 = px.pie(job_levels, names='Job Level', values='Count', title="Job Level Distribution")
    
    # Stacked Bar Chart for Top 5 Programming Skills (Filtered)
    skill_columns = ["PYTHON", "JAVA", "SQL", "JAVASCRIPT", "DJANGO"]
    skill_counts = filtered_df[skill_columns].sum().reset_index()
    skill_counts.columns = ["Skill", "Count"]
    fig3 = px.bar(skill_counts, x='Skill', y='Count', title="Top 5 Programming Skills Demand", color='Count')
    
    # Average Employee Count per Industry (Filtered)
    industry_employee_count = filtered_df.groupby("Industry")["Employee_count"].mean().reset_index()
    fig4 = px.bar(industry_employee_count, x='Industry', y='Employee_count', title="Average Employee Count per Industry", color='Employee_count')
    
    # Top 10 Designations with Most Job Openings (Filtered)
    top_designations = filtered_df["Designation"].value_counts().nlargest(10).reset_index()
    top_designations.columns = ["Designation", "Job Openings"]
    fig5 = px.bar(top_designations, x='Designation', y='Job Openings', title="Top 10 Designations with Most Job Openings", color='Job Openings')
    
    # Total Applicants by Job Location (Unfiltered)
    location_applicants = df.groupby("Location")["Total_applicants"].sum().reset_index()
    fig6 = px.bar(location_applicants, x='Location', y='Total_applicants', title="Total Applicants by Job Location", color='Total_applicants')
    
    # Convert plots to HTML and embed in webpage
    plots = [pio.to_html(fig, full_html=False) for fig in [fig1, fig2, fig3, fig4, fig5]]
    plot6 = pio.to_html(fig6, full_html=False)  # Separate fig6
    
    return render(request, "main/linked_view_charts.html", {"plots": plots, "plot6": plot6, "locations": locations})

# ----------------- End of LinkedIn charts -----------------

#------------------ Pred2 ------------------------------------
def preds2(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            data = df.to_dict(orient='records')  # 转换为字典列表格式
            headers = df.columns.tolist()  # 获取 CSV 列名
            return render(request, 'main/preds2.html', {'data': data, 'headers': headers})
    return render(request, 'main/preds2.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def save_csv2(request):
    if request.method == 'POST':
        csv_content = request.POST.get('csvContent')
        if csv_content:
            # Store the CSV in this directory
            directory = os.path.join(os.getcwd(), 'media', 'downloads')
            os.makedirs(directory, exist_ok=True)

            
            existing_files = os.listdir(directory)
            next_number = len(existing_files) + 1
            filename = f'user{next_number}.csv'
            filepath = os.path.join(directory, filename)

            # Open CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                file.write(csv_content)

            return JsonResponse({'success': True, 'filename': filename})
        return JsonResponse({'success': False, 'error': 'No CSV content provided'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
#---------------------------------------------------------------


from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from io import TextIOWrapper
import csv
import json
import networkx as nx
from neo4j import GraphDatabase

# Connect to Neo4j
driver = settings.NEO4J_DRIVER

@csrf_exempt
def linkedin_upload_csv_file(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        # Assuming the file is uploaded and passed as a CSV
        file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
        csv_reader = csv.reader(file_wrapper)
        header = next(csv_reader)  # Read the header
        
        # Process the CSV file into Neo4j
        linkedin_store_csv_in_neo4j(csv_reader)  
        return redirect('linkedin_graph_visualization')  
    return render(request, 'main/neoinsert2.html')

def linkedin_store_csv_in_neo4j(csv_reader):
    """
    Function to process the CSV file and insert data into Neo4j.
    """
    with driver.session() as session:
        for row in csv_reader:
            company = row[0].strip() if row[0] else None
            designation = row[2].strip() if row[2] else None
            location = row[3].strip() if row[3] else None
            industry = row[9].strip() if row[9] else None
            
            # If any of the required fields are missing, skip this row
            if not company or not designation or not location or not industry:
                print(f"Skipping row due to missing data: {row}")
                continue  # Skip this row if any data is missing
            
            # Now that we've ensured no missing data, pass the values to insert_into_neo4j
            session.execute_write(insert_into_neo4j, company, designation, location, industry)


def insert_into_neo4j(tx, company, designation, location, industry):
    """
    Neo4j Query to insert Company, Designation, Location, and Industry nodes with relationships.
    """
    
    # Debugging: Check if any required field is missing or empty
    print(f"Inserting Data -> Company: {company}, Designation: {designation}, Location: {location}, Industry: {industry}")
    
    # Handle case where company, location, designation, or industry is missing
    if not company or not designation or not location or not industry:
        print("Error: One or more required fields are missing! Skipping insertion.")
        return  # Skip this insertion if any required value is missing
    
    query = """
    MERGE (c:Company {name: $company})
    MERGE (d:Designation {title: $designation})
    MERGE (l:Location {name: $location})
    MERGE (i:Industry {name: $industry})

    MERGE (c)-[:OFFERS]->(d)
    MERGE (d)-[:LOCATED_IN]->(l)
    MERGE (c)-[:PART_OF]->(i)
    """
    
    # Execute the query with provided parameters
    tx.run(query, company=company, designation=designation, location=location, industry=industry)


def linkedin_graph_visualization(request):
    query_type = request.GET.get('query_type', 'LOCATED_IN')  # Default to LOCATED_IN if no query_type is specified
    
    # Define the Cypher queries
    cypher_queries = {
        'LOCATED_IN': "MATCH (n)-[r:LOCATED_IN]->(m) RETURN n.title AS source, type(r) AS relationship, m.name AS target;",
        'OFFERS': "MATCH (n)-[r:OFFERS]->(m) RETURN n.name AS source, type(r) AS relationship, m.title AS target;",
        'PART_OF': "MATCH (n)-[r:PART_OF]->(m) RETURN n.name AS source, type(r) AS relationship, m.name AS target;"
    }
    
    # Get the query based on the selection
    query = cypher_queries.get(query_type, cypher_queries['LOCATED_IN'])

    # Execute the query on Neo4j
    with driver.session() as session:
        result = session.run(query)
        
        graph_data = []
        
        # Print out the results to see the data being returned
        for record in result:
            source = record["source"]
            relationship = record["relationship"]
            target = record["target"]
            
            print(f"Source: {source}, Relationship: {relationship}, Target: {target}")  # Debug log
            
            # If target is null, skip adding that relationship to avoid issues
            if target:
                graph_data.append({
                    "nodes": [
                        {"id": source},
                        {"id": target}
                    ],
                    "relationships": [
                        {"source": source, "relationship": relationship, "target": target}
                    ]
                })
            else:
                print(f"Skipping relationship with null target: {source} - {relationship} - {target}")

    # Print out the final graph_data to debug
    print("Graph Data:", json.dumps(graph_data, indent=4))

    # Convert graph_data to a JSON string and pass it to the template
    graph_data_json = json.dumps(graph_data)

    return render(request, 'main/graph2.html', {"graph_data": graph_data_json, "query_type": query_type})


@csrf_exempt
def linkedin_save_graph_visualization(request):
    """
    Saves the graph visualization as an image.
    """
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            with open('visualization.png', 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            return JsonResponse({'status': 'success', 'message': 'Visualization saved successfully!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No image provided.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
