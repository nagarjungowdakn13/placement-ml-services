from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from rapidfuzz import process
import uvicorn

app = FastAPI(title="Resume NLP Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

skill_corpus = ["Python", "Java", "C++", "SQL", "Machine Learning", "Deep Learning", "Communication", "Leadership", "Teamwork","C#", "JavaScript", "HTML", "CSS", "Django", "Flask", "React", "Node.js", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Linux", "Agile", "Scrum", "Data Analysis", "Data Science", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Tableau", "Power BI", "Excel", "Project Management", "Time Management", "Problem Solving", "Critical Thinking", "Creativity", "Adaptability", "Emotional Intelligence", "Public Speaking", "Negotiation", "Conflict Resolution", "Networking", "Research", "Writing", "Editing", "Marketing", "Sales", "Customer Service", "Business Development", "Financial Analysis", "Accounting", "Budgeting", "Strategic Planning", "Operations Management", "Human Resources", "Recruitment", "Training", "Coaching", "Mentoring", "Event Planning", "Social Media", "SEO", "Content Creation", "Graphic Design", "Video Editing", "Photography", "UX/UI Design", "Mobile Development", "iOS", "Android", "Swift", "Kotlin", "Ruby on Rails", "PHP", "Laravel", "WordPress", "Magento", "Salesforce", "SAP", "Oracle", "Business Intelligence", "Data Warehousing", "ETL", "Big Data", "Hadoop", "Spark", "NoSQL", "MongoDB", "Cassandra", "Redis", "RabbitMQ", "Kafka", "Microservices", "RESTful APIs", "GraphQL", "Web Development", "Software Development", "Quality Assurance", "Testing", "Automation", "CI/CD", "Jenkins", "Travis CI", "CircleCI", "Ansible", "Terraform", "Prometheus", "Grafana", "Splunk", "Log Management", "Cybersecurity", "Penetration Testing", "Ethical Hacking", "Network Security", "Information Security", "Compliance", "Risk Management", "Disaster Recovery", "Business Continuity", "ITIL", "Six Sigma", "Lean", "Kaizen", "Change Management", "Supply Chain Management", "Logistics", "Procurement", "Inventory Management", "Quality Control", "Manufacturing", "Engineering", "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Chemical Engineering", "Biomedical Engineering", "Environmental Science", "Geology", "Meteorology", "Astronomy", "Physics", "Chemistry", "Biology", "Mathematics", "Statistics", "Economics", "Political Science", "Sociology", "Psychology", "Philosophy", "History", "Anthropology", "Linguistics", "Foreign Languages", "Translation", "Interpretation", "Teaching", "Tutoring", "Curriculum Development", "E-learning", "Instructional Design", "Library Science", "Archiving", "Museum Studies", "Urban Planning", "Real Estate", "Architecture", "Interior Design", "Fashion Design", "Culinary Arts", "Hospitality Management", "Tourism", "Event Management", "Public Relations", "Advertising", "Media Planning", "Broadcasting", "Journalism", "Editing", "Publishing", "Legal Research", "Contract Law", "Intellectual Property", "Corporate Law", "Criminal Law", "Family Law", "Environmental Law", "International Law", "Tax Law", "Labor Law", "Civil Rights", "Human Rights", "Nonprofit Management", "Fundraising", "Grant Writing", "Volunteer Management"]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    text_bytes = await file.read()
    text = text_bytes.decode('utf-8', errors='ignore')

    tokens = []
    if nlp is not None:
        try:
            doc = nlp(text)
            tokens = [t.text for t in doc]
        except Exception:
            tokens = text.split()
    else:
        tokens = text.split()

    extracted_skills = set()
    for tok in tokens:
        match = process.extractOne(tok, skill_corpus)
        if match and match[1] >= 85:
            extracted_skills.add(match[0])

    return {"skills": sorted(extracted_skills)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
