from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from stimulsoft_reports.report import StiReport
from stimulsoft_reports.report.enums import StiExportFormat
from stimulsoft_reports.viewer import StiViewer
from fastapi.staticfiles import StaticFiles

# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "Home Page"}


# Ensure the necessary directory structure exists
if not os.path.exists("static/reports"):
    os.makedirs("static/reports")


# Templates directory for rendering HTML pages
templates = Jinja2Templates(directory="templates")


@app.api_route("/viewer", methods=["GET", "POST"])
async def viewer(request: Request):
    # Create a new instance of StiViewer
    viewer = StiViewer()
    viewer.options.appearance.fullScreenMode = True

    # Handle the request to process the report viewer
    if viewer.processRequest(await request.form()):
        return Response(
            content=viewer.getFrameworkResponse(), media_type="application/json"
        )

    # Load the report
    report = StiReport()
    report_path = os.path.join("static", "reports", "campaign.mrt")

    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404, detail=f"The report file '{report_path}' does not exist."
        )

    report.loadFile(report_path)
    viewer.report = report

    # Return the framework response
    return Response(
        content=viewer.getFrameworkResponse(), media_type="application/json"
    )


# async def render_report(request: Request):
#     # Create a new Stimulsoft report instance
#     report = StiReport()

#     # Load the report file (.mrt) from the static directory
#     report_path = "static/reports/campaign.mrt"
#     if not os.path.exists(report_path):
#         raise FileNotFoundError(
#             f"The report file '{report_path}' does not exist. Please ensure the .mrt file is saved in the 'static/reports' directory."
#         )

#     report.loadFile(report_path)

#     # Render the report with the loaded data
#     report.render()

#     # Export the rendered report to HTML format
#     report.exportDocument(StiExportFormat.HTML)

#     # Extract JavaScript and HTML content for rendering
#     js = (
#         report.javascript.getHtml()
#     )  # JavaScript required for displaying the report properly
#     html_content = report.getHtml()  # The main HTML content of the report

#     # Use TemplateResponse to render the page
#     return templates.TemplateResponse(
#         "report.html",
#         {"request": request, "reportJavaScript": js, "reportHtml": html_content},
#     )


# Download report as PDF endpoint
@app.get("/download-report")
async def download_report():
    # Convert report to PDF and return file response
    pdf_file_path = os.path.join("static/reports", "report.pdf")
    return FileResponse(
        pdf_file_path, filename="report.pdf", media_type="application/pdf"
    )
