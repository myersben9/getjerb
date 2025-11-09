# Window sonly
import asyncio, sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.lib.database import JobDatabase
from backend.lib.start_camoufox import startCamoufox
from backend.lib.run_scrape import run_palantir_scrape
from backend.lib.start_camoufox import startCamoufox

db = JobDatabase()
print("Loop policy:", type(asyncio.get_event_loop_policy()).__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with startCamoufox() as camoufox_context:
        app.state.context = camoufox_context      # ✅ attach to app.state
        yield                                     # App runs while this context is alive
    # Shutdown
    app.state.context = None
    await db.close()

app = FastAPI(
    title="JobHub API",
    version="1.0.0",
    lifespan=lifespan, 
)


@app.get("/")
async def root():
    return {"message": "JobHub API is running 🚀"}

@app.post("/scrape")
async def scrape(request: Request):
    context = request.app.state.context
    if context is None:
        return JSONResponse(
            {"status": "error", "message": "Camoufox not initialized."},
            status_code=500,
        )
    asyncio.create_task(run_palantir_scrape(context))
    return JSONResponse(
        {"status": "started", "message": "Palantir scraper running in background."}
    )
@app.get("/jobs")
async def get_jobs(company: str | None = None):
    db = JobDatabase()
    jobs = await db.get_all_jobs(company)
    await db.close()
    return jobs