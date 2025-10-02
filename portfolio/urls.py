from django.urls import path
import portfolio.views as view

urlpatterns = [path("all_projects", view.all_projects, name="all_projects"),
               path("my_projects", view.my_projects, name="my_projects"),
               path("detail_project/<int:project_id>", view.detail_project, name="detail_project"),
               path("load_project", view.load_project, name="load_project"),
               path("redact_project/<int:project_id>", view.redact_project, name="redact_project"),
               path("delete_project/<int:project_id>", view.delete_project, name="delete_project"),
               path("add_dopfile/<int:project_id>", view.add_dopfile, name="add_dopfile"),
               path("delete_dopfile/<int:dopfile_id>", view.delete_dopfile, name="delete_dopfile")]

app_name = "portfolio"
