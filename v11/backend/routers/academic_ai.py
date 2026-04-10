"""
SportAI Suite — Academic Programs Module
Sprint 6 · NXS National Complex
High school, college, and university partnerships
Scholarship hours tracking · Recruiting match engine · Academic scheduling
Team block reservations · Compliance · AI-powered partner briefs

Add to main.py:
    from routers.academic_ai import router as academic_router
    app.include_router(academic_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time, timedelta
from typing import Optional
import random

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, Date, DateTime, Enum as SAEnum, Float,
    ForeignKey, Integer, String, Text, Time, func, select, and_
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class InstitutionLevel(str, enum.Enum):
    HIGH_SCHOOL  = "high_school"
    COMMUNITY    = "community_college"
    COLLEGE      = "college"
    UNIVERSITY   = "university"
    CLUB_PROGRAM = "club_program"


class PartnerStatus(str, enum.Enum):
    PROSPECT    = "prospect"
    NEGOTIATING = "negotiating"
    ACTIVE      = "active"
    RENEWAL     = "renewal"
    LAPSED      = "lapsed"


class Sport(str, enum.Enum):
    FLAG_FOOTBALL = "flag_football"
    SOCCER        = "soccer"
    LACROSSE      = "lacrosse"
    VOLLEYBALL    = "volleyball"
    SOFTBALL      = "softball"
    BASKETBALL    = "basketball"
    PICKLEBALL    = "pickleball"
    ROBOTICS      = "robotics"
    ICE_HOCKEY    = "ice_hockey"
    MULTI_SPORT   = "multi_sport"


class ScholarshipType(str, enum.Enum):
    PRACTICE_HOURS   = "practice_hours"    # Facility time given at no charge
    TOURNAMENT_ENTRY = "tournament_entry"  # Discounted/free tournament registration
    EQUIPMENT_ACCESS = "equipment_access"  # Equipment exchange program
    COACHING_CLINIC  = "coaching_clinic"   # Free coaching clinics
    GAME_FILM        = "game_film"         # TrackMan / facility analytics access


class RecruitingMatchStatus(str, enum.Enum):
    PENDING   = "pending"
    CONTACTED = "contacted"
    VISITED   = "visited"
    COMMITTED = "committed"
    DECLINED  = "declined"


class BlockStatus(str, enum.Enum):
    CONFIRMED   = "confirmed"
    TENTATIVE   = "tentative"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"


class ComplianceType(str, enum.Enum):
    MOU_RENEWAL       = "mou_renewal"
    LIABILITY_WAIVER  = "liability_waiver"
    INSURANCE_CERT    = "insurance_cert"
    ACADEMIC_STANDING = "academic_standing"
    BACKGROUND_CHECK  = "background_check"


# ── ORM Models ────────────────────────────────────────────────────────────────

class AcademicPartner(Base):
    """Institution partnered with NXS for athletic programs."""
    __tablename__ = "academic_partners"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str]            = mapped_column(SAEnum(InstitutionLevel), nullable=False)
    city: Mapped[str]             = mapped_column(String(100), nullable=False)
    state: Mapped[str]            = mapped_column(String(10), default="MN")
    primary_contact: Mapped[str]  = mapped_column(String(200), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str]           = mapped_column(SAEnum(PartnerStatus), default=PartnerStatus.PROSPECT)
    sports: Mapped[str]           = mapped_column(String(500), nullable=False)   # comma-separated
    student_athletes: Mapped[int] = mapped_column(Integer, default=0)
    annual_contract_value: Mapped[float] = mapped_column(Float, default=0.0)
    partnership_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    partnership_end: Mapped[Optional[date]]   = mapped_column(Date, nullable=True)
    scholarship_hours_granted: Mapped[float]  = mapped_column(Float, default=0.0)
    scholarship_hours_used: Mapped[float]     = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]]              = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]                   = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]              = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]              = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    scholarship_hours: Mapped[list["ScholarshipHour"]]         = relationship("ScholarshipHour", back_populates="partner", cascade="all, delete-orphan")
    recruiting_matches: Mapped[list["RecruitingMatch"]]        = relationship("RecruitingMatch", back_populates="partner", cascade="all, delete-orphan")
    schedule_blocks: Mapped[list["AcademicScheduleBlock"]]     = relationship("AcademicScheduleBlock", back_populates="partner", cascade="all, delete-orphan")
    compliance_records: Mapped[list["AcademicComplianceRecord"]] = relationship("AcademicComplianceRecord", back_populates="partner", cascade="all, delete-orphan")

    @property
    def scholarship_hours_remaining(self) -> float:
        return max(0.0, round(self.scholarship_hours_granted - self.scholarship_hours_used, 1))

    @property
    def scholarship_utilization_pct(self) -> float:
        if self.scholarship_hours_granted <= 0:
            return 0.0
        return round(self.scholarship_hours_used / self.scholarship_hours_granted * 100, 1)

    @property
    def days_until_expiry(self) -> Optional[int]:
        if not self.partnership_end:
            return None
        return (self.partnership_end - date.today()).days

    @property
    def is_renewal_due(self) -> bool:
        d = self.days_until_expiry
        return d is not None and 0 <= d <= 90


class ScholarshipHour(Base):
    """Facility scholarship hours granted to academic partners."""
    __tablename__ = "scholarship_hours"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id: Mapped[str]       = mapped_column(ForeignKey("academic_partners.id"), nullable=False)
    scholarship_type: Mapped[str] = mapped_column(SAEnum(ScholarshipType), nullable=False)
    sport: Mapped[str]            = mapped_column(SAEnum(Sport), nullable=False)
    hours_granted: Mapped[float]  = mapped_column(Float, nullable=False)
    hours_used: Mapped[float]     = mapped_column(Float, default=0.0)
    dollar_value: Mapped[float]   = mapped_column(Float, nullable=False)  # $ value at standard rate
    grant_date: Mapped[date]      = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]]  = mapped_column(String(300), nullable=True)
    approved_by: Mapped[Optional[str]]  = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())

    partner: Mapped["AcademicPartner"] = relationship("AcademicPartner", back_populates="scholarship_hours")


class RecruitingMatch(Base):
    """AI-matched recruiting connection — athlete to college/university program."""
    __tablename__ = "recruiting_matches"

    id: Mapped[str]                  = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id: Mapped[str]          = mapped_column(ForeignKey("academic_partners.id"), nullable=False)
    athlete_name: Mapped[str]        = mapped_column(String(200), nullable=False)
    athlete_school: Mapped[str]      = mapped_column(String(200), nullable=False)
    athlete_grad_year: Mapped[int]   = mapped_column(Integer, nullable=False)
    sport: Mapped[str]               = mapped_column(SAEnum(Sport), nullable=False)
    gpa: Mapped[Optional[float]]     = mapped_column(Float, nullable=True)
    match_score: Mapped[int]         = mapped_column(Integer, nullable=False)   # 0–100
    status: Mapped[str]              = mapped_column(SAEnum(RecruitingMatchStatus), default=RecruitingMatchStatus.PENDING)
    match_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contacted_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    visit_date: Mapped[Optional[date]]     = mapped_column(Date, nullable=True)
    outcome_notes: Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    partner: Mapped["AcademicPartner"] = relationship("AcademicPartner", back_populates="recruiting_matches")


class AcademicScheduleBlock(Base):
    """Reserved facility time for academic partner practice or games."""
    __tablename__ = "academic_schedule_blocks"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id: Mapped[str]       = mapped_column(ForeignKey("academic_partners.id"), nullable=False)
    sport: Mapped[str]            = mapped_column(SAEnum(Sport), nullable=False)
    block_date: Mapped[date]      = mapped_column(Date, nullable=False)
    start_time: Mapped[time]      = mapped_column(Time, nullable=False)
    end_time: Mapped[time]        = mapped_column(Time, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    facility_area: Mapped[str]    = mapped_column(String(100), nullable=False)   # "Large Dome", "Small Dome", "Rink", etc.
    status: Mapped[str]           = mapped_column(SAEnum(BlockStatus), default=BlockStatus.CONFIRMED)
    is_scholarship: Mapped[bool]  = mapped_column(Boolean, default=False)       # Counts against scholarship hours
    rate_per_hour: Mapped[float]  = mapped_column(Float, default=0.0)
    revenue: Mapped[float]        = mapped_column(Float, default=0.0)
    attendees: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]]     = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())

    partner: Mapped["AcademicPartner"] = relationship("AcademicPartner", back_populates="schedule_blocks")


class AcademicComplianceRecord(Base):
    """Compliance documents and renewals for academic partners."""
    __tablename__ = "academic_compliance_records"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id: Mapped[str]       = mapped_column(ForeignKey("academic_partners.id"), nullable=False)
    compliance_type: Mapped[str]  = mapped_column(SAEnum(ComplianceType), nullable=False)
    status: Mapped[str]           = mapped_column(String(50), nullable=False)   # current, due_soon, overdue, submitted
    due_date: Mapped[Optional[date]]       = mapped_column(Date, nullable=True)
    submitted_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]]    = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]]           = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())

    partner: Mapped["AcademicPartner"] = relationship("AcademicPartner", back_populates="compliance_records")


# ── Pydantic ──────────────────────────────────────────────────────────────────

class PartnerCreate(BaseModel):
    institution_name: str
    level: InstitutionLevel
    city: str
    state: str = "MN"
    primary_contact: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    sports: str                   # comma-separated
    student_athletes: int = 0
    annual_contract_value: float = 0.0
    partnership_start: Optional[date] = None
    partnership_end: Optional[date] = None
    scholarship_hours_granted: float = 0.0
    notes: Optional[str] = None


class PartnerUpdate(BaseModel):
    status: Optional[PartnerStatus] = None
    scholarship_hours_used: Optional[float] = None
    annual_contract_value: Optional[float] = None
    notes: Optional[str] = None


class ScheduleBlockCreate(BaseModel):
    partner_id: str
    sport: Sport
    block_date: date
    start_time: time
    end_time: time
    facility_area: str
    is_scholarship: bool = False
    rate_per_hour: float = 0.0
    attendees: Optional[int] = None
    notes: Optional[str] = None


class RecruitingMatchCreate(BaseModel):
    partner_id: str
    athlete_name: str
    athlete_school: str
    athlete_grad_year: int
    sport: Sport
    gpa: Optional[float] = None
    match_score: int
    match_rationale: Optional[str] = None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/academic", tags=["Academic Programs"])
claude = Anthropic()

ACADEMIC_CONTEXT = """
You are the AI academic partnerships advisor for NXS National Complex, Proctor MN (704 Kirkus St).
NXS partners with high schools, colleges, and universities to provide elite athletic training facilities.
The campus includes: Large Dome 171,700 sqft, Small Dome 36,100 sqft, Health Center 15,700 sqft,
2 outdoor soccer fields, Ice Rink (200x85), TrackMan golf bays, PuttView AR.
LPF (Level Playing Field Foundation) provides scholarship hours for qualifying athletes.
8 primary sports: flag football, soccer, lacrosse, volleyball, softball, basketball, pickleball, robotics.
The recruiting match engine connects high school athletes with college programs.
Provide specific, actionable insights for growing academic partnerships and scholarship impact.
"""

FACILITY_AREAS = ["Large Dome", "Small Dome", "Health Center", "Outdoor Field 1",
                  "Outdoor Field 2", "Ice Rink", "Skill Shot Academy", "PuttView AR"]


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed academic partners, scholarship hours, recruiting matches, and schedule blocks")
async def seed_academic(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(AcademicPartner))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} partners exist", "seeded": False}

    today = date.today()
    random.seed(55)

    # ── Academic Partners ─────────────────────────────────────────────────────
    partners_data = [
        # High Schools — regional
        dict(institution_name="Proctor High School",         level=InstitutionLevel.HIGH_SCHOOL,  city="Proctor",       sports="soccer,volleyball,basketball,softball", student_athletes=85,  annual_contract_value=18_000, partnership_start=today - timedelta(days=365), partnership_end=today + timedelta(days=180), scholarship_hours_granted=120.0, scholarship_hours_used=78.0, status=PartnerStatus.ACTIVE,  primary_contact="Coach Dan Meyer",        contact_email="dmeyer@proctor.k12.mn.us"),
        dict(institution_name="Duluth East High School",     level=InstitutionLevel.HIGH_SCHOOL,  city="Duluth",        sports="basketball,volleyball,soccer,lacrosse", student_athletes=140, annual_contract_value=24_000, partnership_start=today - timedelta(days=300), partnership_end=today + timedelta(days=65),  scholarship_hours_granted=180.0, scholarship_hours_used=155.0, status=PartnerStatus.RENEWAL, primary_contact="AD Sarah Johnson",       contact_email="sjohnson@isd709.org"),
        dict(institution_name="Hermantown High School",      level=InstitutionLevel.HIGH_SCHOOL,  city="Hermantown",    sports="ice_hockey,volleyball,softball,soccer",  student_athletes=110, annual_contract_value=21_000, partnership_start=today - timedelta(days=200), partnership_end=today + timedelta(days=165), scholarship_hours_granted=150.0, scholarship_hours_used=62.0, status=PartnerStatus.ACTIVE,  primary_contact="Coach Erik Nilsson",     contact_email="enilsson@hermantown.k12.mn.us"),
        dict(institution_name="Cloquet High School",         level=InstitutionLevel.HIGH_SCHOOL,  city="Cloquet",       sports="soccer,flag_football,basketball",        student_athletes=75,  annual_contract_value=14_400, partnership_start=today - timedelta(days=180), partnership_end=today + timedelta(days=185), scholarship_hours_granted=96.0,  scholarship_hours_used=44.0, status=PartnerStatus.ACTIVE,  primary_contact="Coach Amy Strand",       contact_email="astrand@isd94.org"),
        dict(institution_name="Duluth Central High School",  level=InstitutionLevel.HIGH_SCHOOL,  city="Duluth",        sports="basketball,volleyball,robotics,pickleball", student_athletes=95, annual_contract_value=16_800, partnership_start=today - timedelta(days=90), partnership_end=today + timedelta(days=275), scholarship_hours_granted=108.0, scholarship_hours_used=22.0, status=PartnerStatus.ACTIVE, primary_contact="AD Marcus Rivera",       contact_email="mrivera@isd709.org"),
        dict(institution_name="Two Harbors High School",     level=InstitutionLevel.HIGH_SCHOOL,  city="Two Harbors",   sports="soccer,softball,volleyball",             student_athletes=55,  annual_contract_value=9_600,  partnership_start=today + timedelta(days=10), partnership_end=today + timedelta(days=375), scholarship_hours_granted=72.0, scholarship_hours_used=0.0, status=PartnerStatus.NEGOTIATING, primary_contact="Coach Leah Lindqvist", contact_email="llindqvist@isd381.org"),
        # Colleges / Universities
        dict(institution_name="University of Minnesota Duluth", level=InstitutionLevel.UNIVERSITY, city="Duluth",       sports="ice_hockey,volleyball,soccer,basketball", student_athletes=280, annual_contract_value=52_000, partnership_start=today - timedelta(days=400), partnership_end=today + timedelta(days=255), scholarship_hours_granted=300.0, scholarship_hours_used=218.0, status=PartnerStatus.ACTIVE, primary_contact="Athletic Dir. Tom Magnusson", contact_email="tmagnusson@d.umn.edu"),
        dict(institution_name="Lake Superior College",        level=InstitutionLevel.COMMUNITY,   city="Duluth",        sports="soccer,volleyball,basketball",           student_athletes=90,  annual_contract_value=19_200, partnership_start=today - timedelta(days=150), partnership_end=today + timedelta(days=215), scholarship_hours_granted=120.0, scholarship_hours_used=67.0, status=PartnerStatus.ACTIVE, primary_contact="Coach Priya Patel",      contact_email="ppatel@lsc.edu"),
        dict(institution_name="Fond du Lac Tribal College",   level=InstitutionLevel.COMMUNITY,   city="Cloquet",       sports="basketball,soccer,lacrosse",             student_athletes=45,  annual_contract_value=8_400,  partnership_start=today - timedelta(days=60),  partnership_end=today + timedelta(days=305), scholarship_hours_granted=60.0,  scholarship_hours_used=18.0, status=PartnerStatus.ACTIVE, primary_contact="Athletic Coord. Ben Cloud", contact_email="bcloud@fdltcc.edu"),
        dict(institution_name="College of St. Scholastica",   level=InstitutionLevel.COLLEGE,     city="Duluth",        sports="volleyball,soccer,softball,basketball",  student_athletes=165, annual_contract_value=31_200, partnership_start=today - timedelta(days=500), partnership_end=today + timedelta(days=120), scholarship_hours_granted=200.0, scholarship_hours_used=188.0, status=PartnerStatus.RENEWAL, primary_contact="AD Jennifer Walsh",      contact_email="jwalsh@css.edu"),
        dict(institution_name="Northland Community College",  level=InstitutionLevel.COMMUNITY,   city="Thief River Falls", sports="basketball,volleyball,soccer",       student_athletes=60,  annual_contract_value=0.0,    partnership_start=None, partnership_end=None, scholarship_hours_granted=0.0, scholarship_hours_used=0.0, status=PartnerStatus.PROSPECT, primary_contact="Coach Dale Peterson", contact_email="dpeterson@northlandcollege.edu"),
    ]

    created_partners = []
    for pd in partners_data:
        p = AcademicPartner(**pd)
        db.add(p)
        created_partners.append(p)

    await db.flush()

    # ── Scholarship hours ─────────────────────────────────────────────────────
    sch_seeds = []
    for partner in created_partners[:9]:   # active/renewal only
        if partner.scholarship_hours_granted > 0:
            sh = ScholarshipHour(
                partner_id=partner.id,
                scholarship_type=ScholarshipType.PRACTICE_HOURS,
                sport=Sport(random.choice(["soccer","volleyball","basketball","ice_hockey","lacrosse"])),
                hours_granted=partner.scholarship_hours_granted,
                hours_used=partner.scholarship_hours_used,
                dollar_value=round(partner.scholarship_hours_granted * 150.0, 2),  # $150/hr facility rate
                grant_date=partner.partnership_start or today - timedelta(days=180),
                expiry_date=partner.partnership_end,
                approved_by="Shaun Marline — NXS Executive Director",
            )
            db.add(sh)
            sch_seeds.append(sh)

    # ── Schedule blocks — next 30 days ────────────────────────────────────────
    active_partners = [p for p in created_partners if p.status in [PartnerStatus.ACTIVE, PartnerStatus.RENEWAL]]
    blocks_created = 0
    for days_ahead in range(0, 30):
        bdate = today + timedelta(days=days_ahead)
        dow = bdate.weekday()
        if dow >= 5:   # lighter weekend schedule
            if random.random() < 0.4:
                partner = random.choice(active_partners)
                sp_list = partner.sports.split(",")
                sp = random.choice(sp_list).strip()
                try:
                    sport_enum = Sport(sp)
                except ValueError:
                    sport_enum = Sport.MULTI_SPORT
                start_h = random.choice([8, 9, 10])
                dur = random.choice([1.5, 2.0, 2.5])
                end_h = start_h + int(dur)
                area = "Large Dome" if sport_enum in [Sport.SOCCER, Sport.FLAG_FOOTBALL] else ("Ice Rink" if sport_enum == Sport.ICE_HOCKEY else "Small Dome")
                is_sch = partner.scholarship_hours_remaining > 0 and random.random() < 0.6
                rate = 0.0 if is_sch else 150.0
                revenue = 0.0 if is_sch else round(rate * dur, 2)
                block = AcademicScheduleBlock(
                    partner_id=partner.id, sport=sport_enum,
                    block_date=bdate, start_time=time(start_h, 0), end_time=time(end_h, 0),
                    duration_hours=dur, facility_area=area,
                    is_scholarship=is_sch, rate_per_hour=rate, revenue=revenue,
                    attendees=random.randint(12, 35),
                    status=BlockStatus.CONFIRMED,
                )
                db.add(block)
                blocks_created += 1
        else:
            # 2–3 blocks on weekdays
            for _ in range(random.randint(1, 3)):
                partner = random.choice(active_partners)
                sp_list = partner.sports.split(",")
                sp = random.choice(sp_list).strip()
                try:
                    sport_enum = Sport(sp)
                except ValueError:
                    sport_enum = Sport.MULTI_SPORT
                start_h = random.choice([6, 7, 15, 16, 17])
                dur = random.choice([1.0, 1.5, 2.0])
                end_h_val = start_h + int(dur)
                area = "Large Dome" if sport_enum in [Sport.SOCCER, Sport.FLAG_FOOTBALL] else ("Ice Rink" if sport_enum == Sport.ICE_HOCKEY else random.choice(["Small Dome", "Large Dome"]))
                is_sch = partner.scholarship_hours_remaining > 0 and random.random() < 0.5
                rate = 0.0 if is_sch else 150.0
                revenue = 0.0 if is_sch else round(rate * dur, 2)
                block = AcademicScheduleBlock(
                    partner_id=partner.id, sport=sport_enum,
                    block_date=bdate, start_time=time(start_h, 0), end_time=time(min(end_h_val, 22), 0),
                    duration_hours=dur, facility_area=area,
                    is_scholarship=is_sch, rate_per_hour=rate, revenue=revenue,
                    attendees=random.randint(10, 28),
                    status=BlockStatus.CONFIRMED,
                )
                db.add(block)
                blocks_created += 1

    # ── Recruiting matches ─────────────────────────────────────────────────────
    college_partners = [p for p in created_partners if p.level in [InstitutionLevel.UNIVERSITY, InstitutionLevel.COLLEGE, InstitutionLevel.COMMUNITY]]
    athlete_pool = [
        ("Jordan Williams",  "Hermantown HS",    2026, Sport.ICE_HOCKEY,  3.5, 88),
        ("Aaliyah Rivera",   "Proctor HS",       2026, Sport.VOLLEYBALL,  3.9, 92),
        ("Marcus Johnson",   "Duluth East HS",   2025, Sport.BASKETBALL,  3.7, 85),
        ("Sierra Thompson",  "Duluth Central HS",2027, Sport.SOFTBALL,    3.8, 79),
        ("Devon Kowalski",   "Cloquet HS",       2026, Sport.SOCCER,      3.4, 76),
        ("Priya Patel",      "Duluth East HS",   2025, Sport.VOLLEYBALL,  4.0, 94),
        ("Elijah Carter",    "Hermantown HS",    2026, Sport.LACROSSE,    3.3, 71),
        ("Imani Brooks",     "Duluth East HS",   2026, Sport.VOLLEYBALL,  3.7, 86),
        ("Nathan Lindqvist", "Duluth Central HS",2027, Sport.BASKETBALL,  3.2, 68),
        ("Zoe Magnusson",    "Hermantown HS",    2026, Sport.SOCCER,      4.0, 90),
    ]
    statuses = [RecruitingMatchStatus.PENDING, RecruitingMatchStatus.CONTACTED, RecruitingMatchStatus.VISITED, RecruitingMatchStatus.COMMITTED]
    matches_created = 0
    for athlete_name, school, grad_year, sport, gpa, score in athlete_pool:
        # Match each athlete to 1–2 college programs
        for college in random.sample(college_partners, min(2, len(college_partners))):
            st = random.choice(statuses)
            m = RecruitingMatch(
                partner_id=college.id,
                athlete_name=athlete_name, athlete_school=school,
                athlete_grad_year=grad_year, sport=sport, gpa=gpa,
                match_score=score + random.randint(-8, 8),
                status=st,
                match_rationale=f"Strong {sport.value.replace('_',' ')} prospect matching {college.institution_name}'s program needs. GPA {gpa} meets academic threshold.",
                contacted_date=today - timedelta(days=random.randint(5, 45)) if st != RecruitingMatchStatus.PENDING else None,
                visit_date=today - timedelta(days=random.randint(5, 20)) if st in [RecruitingMatchStatus.VISITED, RecruitingMatchStatus.COMMITTED] else None,
            )
            db.add(m)
            matches_created += 1

    # ── Compliance records ────────────────────────────────────────────────────
    compliance_created = 0
    for partner in created_partners[:9]:
        for ctype, status, days_offset in [
            (ComplianceType.MOU_RENEWAL,      "current",  120),
            (ComplianceType.LIABILITY_WAIVER, "current",  200),
            (ComplianceType.INSURANCE_CERT,   "due_soon", 25),
        ]:
            rec = AcademicComplianceRecord(
                partner_id=partner.id,
                compliance_type=ctype,
                status=status if partner.status == PartnerStatus.ACTIVE else ("due_soon" if ctype == ComplianceType.MOU_RENEWAL else "current"),
                due_date=today + timedelta(days=days_offset),
                expiry_date=partner.partnership_end,
            )
            db.add(rec)
            compliance_created += 1

    await db.commit()
    return {
        "message": "Academic Programs seeded",
        "partners": len(partners_data),
        "scholarship_records": len(sch_seeds),
        "schedule_blocks": blocks_created,
        "recruiting_matches": matches_created,
        "compliance_records": compliance_created,
        "seeded": True,
    }


# ── Partners ──────────────────────────────────────────────────────────────────

@router.get("/partners", summary="List all academic partners")
async def list_partners(
    level: Optional[InstitutionLevel] = Query(None),
    status: Optional[PartnerStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(AcademicPartner).where(AcademicPartner.is_active == True)
    if level:  q = q.where(AcademicPartner.level == level)
    if status: q = q.where(AcademicPartner.status == status)
    q = q.order_by(AcademicPartner.annual_contract_value.desc())
    result = await db.execute(q)
    partners = result.scalars().unique().all()
    return [
        {"id": p.id, "institution_name": p.institution_name, "level": p.level,
         "city": p.city, "state": p.state, "status": p.status,
         "primary_contact": p.primary_contact, "contact_email": p.contact_email,
         "sports": p.sports.split(","),
         "student_athletes": p.student_athletes,
         "annual_contract_value": p.annual_contract_value,
         "partnership_start": p.partnership_start.isoformat() if p.partnership_start else None,
         "partnership_end": p.partnership_end.isoformat() if p.partnership_end else None,
         "scholarship_hours_granted": p.scholarship_hours_granted,
         "scholarship_hours_used": p.scholarship_hours_used,
         "scholarship_hours_remaining": p.scholarship_hours_remaining,
         "scholarship_utilization_pct": p.scholarship_utilization_pct,
         "days_until_expiry": p.days_until_expiry,
         "is_renewal_due": p.is_renewal_due}
        for p in partners
    ]


@router.post("/partners", summary="Add a new academic partner")
async def create_partner(payload: PartnerCreate, db: AsyncSession = Depends(get_db)) -> dict:
    partner = AcademicPartner(**payload.model_dump())
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return {"id": partner.id, "institution_name": partner.institution_name, "message": "Partner added"}


@router.patch("/partners/{partner_id}", summary="Update partner status or scholarship hours")
async def update_partner(partner_id: str, payload: PartnerUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(AcademicPartner).where(AcademicPartner.id == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(404, "Partner not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(partner, k, v)
    await db.commit()
    return {"id": partner.id, "message": "Partner updated"}


# ── Scholarship Hours ─────────────────────────────────────────────────────────

@router.get("/scholarship-hours", summary="Scholarship hours by partner — utilization and remaining")
async def scholarship_hours_summary(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(AcademicPartner).where(
        AcademicPartner.scholarship_hours_granted > 0,
        AcademicPartner.is_active == True,
    ))
    partners = result.scalars().all()

    total_granted = sum(p.scholarship_hours_granted for p in partners)
    total_used    = sum(p.scholarship_hours_used for p in partners)
    total_dollar  = round(total_granted * 150.0, 2)

    expiring = [p for p in partners if p.is_renewal_due]
    low_util = [p for p in partners if p.scholarship_utilization_pct < 40 and p.scholarship_hours_granted > 0]

    return {
        "total_hours_granted": round(total_granted, 1),
        "total_hours_used":    round(total_used, 1),
        "total_hours_remaining": round(total_granted - total_used, 1),
        "overall_utilization_pct": round(total_used / total_granted * 100, 1) if total_granted else 0,
        "dollar_value_granted": total_dollar,
        "dollar_value_used": round(total_used * 150.0, 2),
        "partners_expiring_90d": len(expiring),
        "partners_low_utilization": len(low_util),
        "partner_detail": [
            {"id": p.id, "institution_name": p.institution_name, "level": p.level,
             "hours_granted": p.scholarship_hours_granted, "hours_used": p.scholarship_hours_used,
             "hours_remaining": p.scholarship_hours_remaining,
             "utilization_pct": p.scholarship_utilization_pct,
             "days_until_expiry": p.days_until_expiry, "is_renewal_due": p.is_renewal_due}
            for p in sorted(partners, key=lambda x: x.scholarship_utilization_pct, reverse=True)
        ],
    }


# ── Scheduling ────────────────────────────────────────────────────────────────

@router.get("/schedule", summary="Upcoming academic schedule blocks")
async def academic_schedule(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    partner_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    today = date.today()
    fd = from_date or today
    td = to_date or today + timedelta(days=14)
    q = select(AcademicScheduleBlock).where(
        AcademicScheduleBlock.block_date >= fd,
        AcademicScheduleBlock.block_date <= td,
        AcademicScheduleBlock.status != BlockStatus.CANCELLED,
    )
    if partner_id:
        q = q.where(AcademicScheduleBlock.partner_id == partner_id)
    q = q.order_by(AcademicScheduleBlock.block_date, AcademicScheduleBlock.start_time)
    result = await db.execute(q)
    blocks = result.scalars().all()
    return [
        {"id": b.id, "partner_id": b.partner_id, "sport": b.sport,
         "block_date": b.block_date.isoformat(),
         "start_time": b.start_time.strftime("%H:%M"),
         "end_time": b.end_time.strftime("%H:%M"),
         "duration_hours": b.duration_hours,
         "facility_area": b.facility_area, "status": b.status,
         "is_scholarship": b.is_scholarship,
         "rate_per_hour": b.rate_per_hour, "revenue": b.revenue,
         "attendees": b.attendees}
        for b in blocks
    ]


@router.post("/schedule", summary="Book an academic facility block")
async def create_block(payload: ScheduleBlockCreate, db: AsyncSession = Depends(get_db)) -> dict:
    start_dt = datetime.combine(date.today(), payload.start_time)
    end_dt   = datetime.combine(date.today(), payload.end_time)
    hours    = (end_dt - start_dt).seconds / 3600
    revenue  = 0.0 if payload.is_scholarship else round(payload.rate_per_hour * hours, 2)
    block    = AcademicScheduleBlock(
        **payload.model_dump(),
        duration_hours=hours, revenue=revenue,
    )
    db.add(block)
    await db.commit()
    return {"id": block.id, "revenue": revenue, "duration_hours": hours, "message": "Block reserved"}


# ── Recruiting ────────────────────────────────────────────────────────────────

@router.get("/recruiting-matches", summary="Recruiting match pipeline")
async def recruiting_matches(
    status: Optional[RecruitingMatchStatus] = Query(None),
    sport: Optional[Sport] = Query(None),
    min_score: int = Query(0),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(RecruitingMatch)
    if status:    q = q.where(RecruitingMatch.status == status)
    if sport:     q = q.where(RecruitingMatch.sport == sport)
    if min_score: q = q.where(RecruitingMatch.match_score >= min_score)
    q = q.order_by(RecruitingMatch.match_score.desc())
    result = await db.execute(q)
    matches = result.scalars().all()
    return [
        {"id": m.id, "partner_id": m.partner_id,
         "athlete_name": m.athlete_name, "athlete_school": m.athlete_school,
         "athlete_grad_year": m.athlete_grad_year, "sport": m.sport,
         "gpa": m.gpa, "match_score": m.match_score, "status": m.status,
         "match_rationale": m.match_rationale,
         "contacted_date": m.contacted_date.isoformat() if m.contacted_date else None,
         "visit_date": m.visit_date.isoformat() if m.visit_date else None}
        for m in matches
    ]


@router.post("/recruiting-match", summary="Create a recruiting match")
async def create_match(payload: RecruitingMatchCreate, db: AsyncSession = Depends(get_db)) -> dict:
    match = RecruitingMatch(**payload.model_dump())
    db.add(match)
    await db.commit()
    return {"id": match.id, "match_score": payload.match_score, "message": "Match created"}


# ── Compliance ────────────────────────────────────────────────────────────────

@router.get("/compliance", summary="Compliance status across all academic partners")
async def compliance_overview(db: AsyncSession = Depends(get_db)) -> dict:
    q = select(AcademicComplianceRecord)
    result = await db.execute(q)
    records = result.scalars().all()

    overdue  = [r for r in records if r.status == "overdue"]
    due_soon = [r for r in records if r.status == "due_soon"]
    current  = [r for r in records if r.status == "current"]

    return {
        "total_records": len(records),
        "overdue": len(overdue),
        "due_soon": len(due_soon),
        "current": len(current),
        "overdue_records": [{"id": r.id, "partner_id": r.partner_id, "compliance_type": r.compliance_type, "due_date": r.due_date.isoformat() if r.due_date else None} for r in overdue],
        "due_soon_records": [{"id": r.id, "partner_id": r.partner_id, "compliance_type": r.compliance_type, "due_date": r.due_date.isoformat() if r.due_date else None, "days_until_due": (r.due_date - date.today()).days if r.due_date else None} for r in due_soon],
    }


# ── KPIs ──────────────────────────────────────────────────────────────────────

@router.get("/kpis", summary="Academic program KPI snapshot")
async def academic_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    partners_q = await db.execute(select(AcademicPartner).where(AcademicPartner.is_active == True))
    partners = partners_q.scalars().all()

    active    = [p for p in partners if p.status == PartnerStatus.ACTIVE]
    renewal   = [p for p in partners if p.status == PartnerStatus.RENEWAL]
    prospects = [p for p in partners if p.status == PartnerStatus.PROSPECT]

    total_rev       = sum(p.annual_contract_value for p in active + renewal)
    total_athletes  = sum(p.student_athletes for p in active + renewal)
    total_sch_hrs   = sum(p.scholarship_hours_granted for p in partners)
    used_sch_hrs    = sum(p.scholarship_hours_used for p in partners)

    blocks_q = await db.execute(select(func.count(), func.sum(AcademicScheduleBlock.revenue)).where(
        AcademicScheduleBlock.block_date >= date.today(),
        AcademicScheduleBlock.status == BlockStatus.CONFIRMED,
    ))
    blocks_row = blocks_q.one()
    upcoming_blocks, upcoming_revenue = blocks_row[0] or 0, blocks_row[1] or 0.0

    matches_q = await db.execute(select(func.count()).select_from(RecruitingMatch).where(
        RecruitingMatch.status == RecruitingMatchStatus.COMMITTED
    ))
    committed_matches = matches_q.scalar() or 0

    level_q = await db.execute(select(AcademicPartner.level, func.count()).where(AcademicPartner.is_active == True).group_by(AcademicPartner.level))
    level_breakdown = {row[0]: row[1] for row in level_q.all()}

    return {
        "active_partners": len(active),
        "renewal_partners": len(renewal),
        "prospects": len(prospects),
        "total_partner_count": len(partners),
        "annual_contract_revenue": round(total_rev, 2),
        "total_student_athletes": total_athletes,
        "scholarship_hours_granted": round(total_sch_hrs, 1),
        "scholarship_hours_used": round(used_sch_hrs, 1),
        "scholarship_utilization_pct": round(used_sch_hrs / total_sch_hrs * 100, 1) if total_sch_hrs else 0,
        "scholarship_dollar_value": round(total_sch_hrs * 150.0, 2),
        "upcoming_blocks_14d": upcoming_blocks,
        "upcoming_block_revenue": round(upcoming_revenue, 2),
        "committed_recruiting_matches": committed_matches,
        "level_breakdown": level_breakdown,
    }


# ── AI Endpoints ──────────────────────────────────────────────────────────────

@router.post("/ai-partner-brief/{partner_id}", summary="AI brief for individual academic partner")
async def ai_partner_brief(partner_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    p_result = await db.execute(select(AcademicPartner).where(AcademicPartner.id == partner_id))
    partner = p_result.scalar_one_or_none()
    if not partner:
        raise HTTPException(404, "Partner not found")

    matches_q = await db.execute(select(RecruitingMatch).where(RecruitingMatch.partner_id == partner_id))
    matches = matches_q.scalars().all()
    blocks_q = await db.execute(select(AcademicScheduleBlock).where(
        AcademicScheduleBlock.partner_id == partner_id,
        AcademicScheduleBlock.block_date >= date.today(),
    ).order_by(AcademicScheduleBlock.block_date).limit(5))
    upcoming_blocks = blocks_q.scalars().all()

    prompt = f"""
Academic Partner Brief — {partner.institution_name}

PROFILE:
- Level: {partner.level} | City: {partner.city}, {partner.state}
- Sports: {partner.sports}
- Student athletes: {partner.student_athletes}
- Annual contract value: ${partner.annual_contract_value:,.0f}
- Status: {partner.status}
- Partnership: {partner.partnership_start} → {partner.partnership_end} ({partner.days_until_expiry} days remaining)

SCHOLARSHIP HOURS:
- Granted: {partner.scholarship_hours_granted}hr | Used: {partner.scholarship_hours_used}hr | Remaining: {partner.scholarship_hours_remaining}hr
- Utilization: {partner.scholarship_utilization_pct}%
- Dollar value: ${partner.scholarship_hours_granted * 150:,.0f}

RECRUITING PIPELINE: {len(matches)} matches
- Committed: {sum(1 for m in matches if m.status == RecruitingMatchStatus.COMMITTED)}
- Visited: {sum(1 for m in matches if m.status == RecruitingMatchStatus.VISITED)}
- Contacted: {sum(1 for m in matches if m.status == RecruitingMatchStatus.CONTACTED)}

UPCOMING BLOCKS: {len(upcoming_blocks)}
{chr(10).join(f"  {b.block_date} {b.start_time}–{b.end_time}: {b.sport} @ {b.facility_area} ({'scholarship' if b.is_scholarship else f'${b.revenue}'})" for b in upcoming_blocks)}

Generate a 3-paragraph partner brief:
1. Partnership health — contract value, scholarship utilization rate, renewal urgency (if applicable)
2. Facility usage and recruiting performance — how well are they using the facilities and how is the recruiting pipeline performing?
3. Recommended next steps — renewal strategy, scholarship hour push, recruiting match follow-ups, or new program opportunities
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=ACADEMIC_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "partner_id": partner_id,
        "institution_name": partner.institution_name,
        "brief": response.content[0].text,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-program-brief", summary="AI academic program portfolio brief")
async def ai_program_brief(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await academic_kpis(db)
    sch = await scholarship_hours_summary(db)
    compliance = await compliance_overview(db)

    partners_result = await db.execute(select(AcademicPartner).where(AcademicPartner.status == PartnerStatus.RENEWAL))
    renewals = partners_result.scalars().all()

    prompt = f"""
NXS Academic Programs — Portfolio Strategy Brief

PROGRAM KPIs:
- Active partners: {kpis['active_partners']} | Renewal due: {kpis['renewal_partners']} | Prospects: {kpis['prospects']}
- Annual contract revenue: ${kpis['annual_contract_revenue']:,.0f}
- Total student athletes served: {kpis['total_student_athletes']:,}
- Scholarship hours: {kpis['scholarship_hours_granted']} granted / {kpis['scholarship_hours_used']} used ({kpis['scholarship_utilization_pct']}%)
- Scholarship dollar value: ${kpis['scholarship_dollar_value']:,.0f}
- Upcoming facility blocks (14d): {kpis['upcoming_blocks_14d']}
- Committed recruiting matches: {kpis['committed_recruiting_matches']}

LEVEL BREAKDOWN: {kpis['level_breakdown']}

SCHOLARSHIP HEALTH:
- Partners expiring ≤90d: {sch['partners_expiring_90d']}
- Partners with low utilization (<40%): {sch['partners_low_utilization']}

RENEWALS DUE:
{chr(10).join(f"  {p.institution_name} — ${p.annual_contract_value:,.0f}/yr, {p.days_until_expiry} days remaining" for p in renewals)}

COMPLIANCE: {compliance['overdue']} overdue, {compliance['due_soon']} due soon

Generate a 3-paragraph portfolio brief:
1. Program health — contract revenue trajectory, scholarship impact vs grant-reporting potential, level mix balance
2. Renewal urgency — which partnerships need attention in the next 90 days and what's the revenue at risk?
3. Growth strategy — which institution types to target next, how to leverage the recruiting match engine to attract college partners, and what NXS facility advantages (TrackMan, PuttView, dome size) to lead with in prospect conversations
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=ACADEMIC_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "kpis": kpis,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-recruiting-brief", summary="AI recruiting match strategy for a partner")
async def ai_recruiting_brief(
    partner_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    p_result = await db.execute(select(AcademicPartner).where(AcademicPartner.id == partner_id))
    partner = p_result.scalar_one_or_none()
    if not partner:
        raise HTTPException(404, "Partner not found")

    matches_q = await db.execute(select(RecruitingMatch).where(
        RecruitingMatch.partner_id == partner_id
    ).order_by(RecruitingMatch.match_score.desc()))
    matches = matches_q.scalars().all()

    top_matches = "\n".join(
        f"  {m.athlete_name} ({m.athlete_school}, {m.athlete_grad_year}) — {m.sport.value}, GPA {m.gpa}, Score {m.match_score}/100 — {m.status}"
        for m in matches[:8]
    )

    prompt = f"""
Recruiting Brief — {partner.institution_name} ({partner.level})

Program sports: {partner.sports}
Total matches in pipeline: {len(matches)}
Status breakdown: {dict([(s.value, sum(1 for m in matches if m.status == s)) for s in RecruitingMatchStatus])}

Top Athletes by Match Score:
{top_matches}

Generate a concise 2-paragraph recruiting brief:
1. Pipeline assessment — who are the top 3 prospects to prioritize and what's the action for each?
2. How to use NXS facility visits (facility tour, game film session, TrackMan evaluation) to convert contacted athletes to committed, and what communication to send this week
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=ACADEMIC_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "partner_id": partner_id,
        "institution_name": partner.institution_name,
        "brief": response.content[0].text,
        "matches_total": len(matches),
        "generated_at": datetime.utcnow().isoformat(),
    }
