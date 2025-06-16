from django.urls import path
from . import views

urlpatterns = [
    
    path('admin_login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    #dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('businessman_dashboard/', views.businessman_dashboard, name='businessman_dashboard'),
    path('content_creator_dashboard/', views.content_creator_dashboard, name='content_creator_dashboard'),
    path('data-analyst-dashboard/', views.data_analyst_dashboard, name='data_analyst_dashboard'),
    

    #create profile
    path('create_businessman_profile/', views.create_businessman_profile, name='create_profile'),
    path('create_creator_profile/', views.create_creator_profile, name='create_creator_profile'), 
    path('create_analyst_profile/', views.create_analyst_profile, name='create_analyst_profile'),
    
    #profile
    path('view_profile/', views.view_profile_businessman, name= 'view_profile_businessman'),
    path('view_content_creator_profile/', views.view_profile_content_creator, name= 'view_profile_content_creator'),
    path('view_profile_data_analyst/', views.view_profile_data_analyst, name='view_profile_data_analyst'),
    
    #create acc
    path('create_user_account/', views.create_user_account, name='create_user_account'),
    path('create_businessman_account/', views.create_businessman_account,  name='create_businessman_account'),
    path('create_content_creator_account/', views.create_content_creator_account, name='create_content_creator_account'),
    path('create_data_analyst_account/', views.create_data_analyst_account, name='create_data_analyst_account'),
    
    #view user accounts
    path('view_user_accounts/', views.view_user_accounts, name='view_user_accounts'), 
    path('view_businessman_accounts/', views.view_businessman_accounts, name='view_businessman_accounts'),
    path('view_content_creator_accounts/', views.view_content_creator_accounts, name='view_content_creator_accounts'),
    path('view_data_analyst_accounts/', views.view_data_analyst_accounts, name='view_data_analyst_accounts'),
    
    path('categories/', views.category_list, name='category_list'),
    path('create_category/', views.create_category, name='create_category'), 
    path('category/update/<int:category_id>/', views.update_category, name='update_category'),

    path('update_user_account/<int:user_id>/', views.update_user_account, name='update_user_account'),
    

    
    #download csv
    path('download_csv/', views.download_csv, name='download_csv'),
    #upload csv 
    #path('upload_csv_or_xlsx/', views.upload_csv_or_xlsx, name= 'upload_csv_or_xlsx'),

    
    #scrape part
    path('scrape_profile/', views.scrape_profile, name='scrape_profile'),
    path('login_instagram/', views.login_instagram, name='login_instagram'),
    

    path('update_profile/<str:profile_id>/', views.update_profile, name='update_profile'),
    
    
    #landing page
    path('marketing_page/', views.marketing_page, name='marketing_page'),
    path('testimonial_page/', views.testimonial_page, name='testimonial_page'),
    path('login_rate/', views.login_rate, name='login_rate'),
    
    #visibility control
    path('visibility/', views.manage_visibility, name='manage_visibility'),
    path('visibility/<int:data_item_id>/', views.update_visibility, name='update_visibility'),
    
    path('home/', views.home_page, name='home_page'),


    # Instagram CSV edit rows/columns
    path('preds/', views.preds, name='preds'),
    path('predict_engagement/', views.predict_engagement, name='predict_engagement'),
    path('upload_and_view_charts/', views.upload_and_view_charts, name='upload_and_view_charts'),
    
    
    # graph visualize
    path('graph_view/', views.graph_view, name='graph_view'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('save_visualization/', views.save_visualization, name='save_visualization'),
    
    
    
    # LinkedIn ML
    path('train_model/', views.train_model, name='train_model'),
    path('predict_skills/', views.predict_skills_view, name='predict_skills_view'),
    path('get_job_options/', views.get_job_options, name='get_job_options'),  # Ensure this exists

    # LinkedIn Charts
    path('linkedin_charts/', views.handle_linkedin_data, name='linkedin_charts'),
    
    # LinkedIn CSV edit rows/columns + Neo4j
    path('preds2/', views.preds2, name='preds2'),
    path('linkedin_upload_csv_file/', views.linkedin_upload_csv_file, name='linkedin_upload_csv_file'),
    path('linkedin_graph_visualization/', views.linkedin_graph_visualization, name='linkedin_graph_visualization'),
    path('linkedin_save_visualization/', views.linkedin_save_graph_visualization, name='linkedin_save_visualization'),
    
]
