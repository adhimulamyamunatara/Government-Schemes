"""
MyScheme Backend Proxy Server
Converts your working Python scraping code into a REST API for Flutter app
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import time
from collections import deque
import re
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow Flutter app to call this backend

# ===============================
# CONFIG
# ===============================
BASE_URL = "https://api.myscheme.gov.in/schemes/v5/public/schemes"
API_KEY = "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"

headers = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.myscheme.gov.in",
    "user-agent": "Mozilla/5.0",
    "x-api-key": API_KEY
}

# ===============================
# HELPER FUNCTIONS (Your working code!)
# ===============================
def fetch_json(url):
    """Fetch JSON from API with error handling"""
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        print(f"HTTPError: {e} -> {url}")
        return None
    except requests.RequestException as e:
        print(f"RequestException: {e} -> {url}")
        return None


def get_gemini_api_key():
    """Read Gemini API key from environment for local and Render deployments."""
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")


def generate_gemini_reply(message):
    """Generate a Gemini reply using the server-side API key."""
    api_key = get_gemini_api_key()
    if not api_key:
        return None, "Gemini API key not configured"

    try:
        client = genai.Client(api_key=api_key)
        for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=message,
                )
                reply = getattr(response, "text", None) or "Sorry, I could not process that."
                return reply, None
            except Exception as model_error:
                last_error = model_error
                continue

        return None, f"Gemini request failed: {last_error}"
    except Exception as e:
        return None, f"Gemini request failed: {e}"


def find_candidate_lists(obj, key_candidates):
    """Recursively search for lists that look like documents"""
    results = []
    q = deque([obj])
    visited = set()
    while q:
        cur = q.popleft()
        if id(cur) in visited:
            continue
        visited.add(id(cur))
        if isinstance(cur, list):
            sample = [x for x in cur[:5] if isinstance(x, dict)]
            if sample:
                matched = False
                for d in sample:
                    if any(k in d for k in key_candidates):
                        matched = True
                        break
                if matched:
                    results.append(cur)
            for it in cur:
                if isinstance(it, (list, dict)):
                    q.append(it)
        elif isinstance(cur, dict):
            for v in cur.values():
                if isinstance(v, (list, dict)):
                    q.append(v)
    return results


def extract_text_from_rich(node):
    """Extract text from rich content blocks"""
    if node is None:
        return ""
    if isinstance(node, str):
        return node.strip()
    if isinstance(node, dict):
        if "text" in node:
            return node.get("text", "").strip()
        if "children" in node:
            return extract_text_from_rich(node["children"])
        return " ".join(extract_text_from_rich(v) for v in node.values()).strip()
    if isinstance(node, list):
        return "\n".join(extract_text_from_rich(it) for it in node).strip()
    return str(node).strip()


def normalize_documents(resp):
    """Extract document requirements"""
    if not resp:
        return []
    docs = []
    data = resp.get("data", {})
    lang_block = data.get("en") or data.get("hi") or {}
    for block in lang_block.get("documents_required", []):
        for item in block.get("children", []):
            text = extract_text_from_rich(item)
            if text:
                text = re.sub(r'^\d+\.\s*', '', text.strip())
                docs.append(text)
    return docs


def normalize_faqs(resp):
    """Extract FAQs from various formats"""
    if resp is None:
        return []
    
    if isinstance(resp, dict) and "data" in resp and isinstance(resp["data"], (list, dict)):
        candidate = resp["data"]
    else:
        candidate = resp

    faqs = []
    if isinstance(candidate, list):
        for item in candidate:
            if isinstance(item, dict):
                q = item.get("question") or item.get("faqQuestion") or item.get("q") or item.get("faq") or ""
                a = item.get("answer") or item.get("faqAnswer") or item.get("a") or ""
                if isinstance(q, dict) or isinstance(q, list):
                    q = extract_text_from_rich(q)
                if isinstance(a, dict) or isinstance(a, list):
                    a = extract_text_from_rich(a)
                faqs.append({"q": q, "a": a})
            elif isinstance(item, str):
                faqs.append({"q": item, "a": ""})
        return faqs

    if isinstance(candidate, dict):
        lists = find_candidate_lists(candidate, {"question", "faqQuestion", "faq", "answer", "faqAnswer"})
        for L in lists:
            for item in L:
                if isinstance(item, dict):
                    q = item.get("question") or item.get("faqQuestion") or item.get("q") or item.get("faq") or ""
                    a = item.get("answer") or item.get("faqAnswer") or item.get("a") or ""
                    if isinstance(q, (list, dict)):
                        q = extract_text_from_rich(q)
                    if isinstance(a, (list, dict)):
                        a = extract_text_from_rich(a)
                    faqs.append({"q": q, "a": a})
        
        if not faqs:
            for k in ["faqs", "faq", "questions", "data"]:
                if k in candidate and isinstance(candidate[k], list):
                    for item in candidate[k]:
                        if isinstance(item, dict):
                            q = item.get("question") or item.get("faqQuestion") or ""
                            a = item.get("answer") or item.get("faqAnswer") or ""
                            faqs.append({"q": q, "a": a})
    return faqs


# ===============================
# API ENDPOINTS
# ===============================


# ===============================
# API ENDPOINTS
# ===============================

@app.route('/', methods=['GET'])
def api_home():
    """Show available API routes"""

    return jsonify({
        "project": "Community Service Project - Govt Schemes Backend",
        "status": "running",
        "version": "1.0",

        "available_routes": [

            {
                "method": "GET",
                "endpoint": "/health",
                "description": "Check backend health status"
            },

            {
                "method": "GET",
                "endpoint": "/api/schemes",
                "description": "Fetch list of government scheme slugs",
                "example":
                    "/api/schemes?from_index=0&size=10"
            },

            {
                "method": "GET",
                "endpoint": "/api/scheme/<slug>",
                "description": "Fetch complete details of one scheme",
                "example":
                    "/api/scheme/pm-kisan"
            },

            {
                "method": "POST",
                "endpoint": "/api/schemes/batch",
                "description": "Fetch multiple schemes at once",
                "body": {
                    "slugs": [
                        "pm-kisan",
                        "pmkvy-stt"
                    ]
                }
            }
        ],

        "message":
            "Welcome to MyScheme Backend API"
    })




@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "MyScheme Backend Proxy is running!",
        "api_key_configured": bool(API_KEY)
    })


@app.route('/api/schemes', methods=['GET'])
def get_all_schemes():
    """
    Fetch all schemes (paginated)
    Query params:
        - from_index: Starting index (default: 0)
        - size: Number of schemes per page (default: 100)
    """
    try:
        from_index = int(request.args.get('from_index', 0))
        size = int(request.args.get('size', 100))
        
        url = f"https://api.myscheme.gov.in/search/v5/schemes?lang=en&q=%5B%5D&keyword=&sort=&from={from_index}&size={size}"
        resp = fetch_json(url)
        
        if not resp:
            return jsonify({"error": "Failed to fetch schemes"}), 500
        
        all_slugs = []
        if resp.get("data") and resp["data"].get("hits"):
            for item in resp["data"]["hits"]["items"]:
                slug = item["fields"]["slug"]
                all_slugs.append(slug)
        
        total = resp.get('data', {}).get('summary', {}).get('total', 0)
        
        return jsonify({
            "slugs": all_slugs,
            "total": total,
            "from_index": from_index,
            "size": size,
            "returned": len(all_slugs)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/scheme/<slug>', methods=['GET'])
def get_scheme(slug):
    """
    Fetch detailed scheme information by slug
    Example: /api/scheme/pmkvy-stt
    """
    try:
        # Fetch main scheme details
        url = f"{BASE_URL}?slug={slug}&lang=en"
        resp = fetch_json(url)
        
        if not resp:
            return jsonify({"error": f"Scheme '{slug}' not found"}), 404
        
        data = resp.get("data", {})
        en = data.get("en", {})
        scheme_id = data.get("_id")
        
        # Extract references
        references = []
        for i, ref in enumerate(en.get("schemeContent", {}).get("references", [])):
            url_ref = ref.get("url")
            if url_ref:
                references.append({"title": f"Reference {i+1}", "url": url_ref})
        
        # Handle ministry field
        ministry = None
        basic_details = en.get("basicDetails", {})
        nodal_dept = basic_details.get("nodalDepartmentName")
        if isinstance(nodal_dept, dict):
            ministry = nodal_dept.get("label")
        
        # Build scheme object
        scheme = {
            "id": scheme_id,
            "slug": slug,
            "title": basic_details.get("schemeName"),
            "shortTitle": basic_details.get("schemeShortTitle"),
            "description": en.get("schemeContent", {}).get("briefDescription", "").replace('&amp;', '&'),
            "detailedDescription": en.get("schemeContent", {}).get("detailedDescription_md", "").replace('&amp;', '&'),
            "benefits": en.get("schemeContent", {}).get("benefits_md"),
            "eligibility": en.get("eligibilityCriteria", {}).get("eligibilityDescription_md", "").replace('&amp;', '&'),
            "exclusions": en.get("schemeContent", {}).get("exclusions_md", "").replace('&amp;', '&'),
            "ministry": ministry,
            "applicationProcess": (
                en.get("applicationProcess")[0].get("process_md", "").replace('&amp;', '&')
                if en.get("applicationProcess") else None
            ),
            "references": references,
            "documents": [],
            "faqs": []
        }
        
        # Fetch documents and FAQs (if scheme_id exists)
        if scheme_id:
            docs_json = fetch_json(f"{BASE_URL}/{scheme_id}/documents?lang=en")
            faqs_json = fetch_json(f"{BASE_URL}/{scheme_id}/faqs?lang=en")
            
            scheme["documents"] = normalize_documents(docs_json) if docs_json else []
            scheme["faqs"] = normalize_faqs(faqs_json) if faqs_json else []
        
        return jsonify(scheme)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schemes/batch', methods=['POST'])
def get_schemes_batch():
    """
    Fetch multiple schemes at once with FULL details (documents & FAQs)
    Body: {"slugs": ["pmkvy-stt", "pm-kisan", ...]}
    """
    try:
        data = request.get_json()
        slugs = data.get('slugs', [])
        
        if not slugs:
            return jsonify({"error": "No slugs provided"}), 400
        
        all_schemes = []
        
        for slug in slugs:
            try:
                resp = fetch_json(f"{BASE_URL}?slug={slug}&lang=en")
                if not resp:
                    continue
                
                data = resp.get("data", {})
                en = data.get("en", {})
                scheme_id = data.get("_id")
                
                # Extract references
                references = []
                for i, ref in enumerate(en.get("schemeContent", {}).get("references", [])):
                    url_ref = ref.get("url")
                    if url_ref:
                        references.append({"title": f"Reference {i+1}", "url": url_ref})
                
                # Handle ministry field
                ministry = None
                basic_details = en.get("basicDetails", {})
                nodal_dept = basic_details.get("nodalDepartmentName")
                if isinstance(nodal_dept, dict):
                    ministry = nodal_dept.get("label")
                
                scheme = {
                    "id": scheme_id,
                    "slug": slug,
                    "title": basic_details.get("schemeName"),
                    "shortTitle": basic_details.get("schemeShortTitle"),
                    "description": en.get("schemeContent", {}).get("briefDescription", "").replace('&amp;', '&'),
                    "detailedDescription": en.get("schemeContent", {}).get("detailedDescription_md", "").replace('&amp;', '&'),
                    "benefits": en.get("schemeContent", {}).get("benefits_md", ""),
                    "eligibility": en.get("eligibilityCriteria", {}).get("eligibilityDescription_md", "").replace('&amp;', '&'),
                    "exclusions": en.get("schemeContent", {}).get("exclusions_md", "").replace('&amp;', '&'),
                    "ministry": ministry,
                    "applicationProcess": (
                        en.get("applicationProcess")[0].get("process_md", "").replace('&amp;', '&')
                        if en.get("applicationProcess") else ""
                    ),
                    "references": references,
                    "documents": [],
                    "faqs": []
                }
                
                # Fetch documents and FAQs (if scheme_id exists)
                if scheme_id:
                    docs_json = fetch_json(f"{BASE_URL}/{scheme_id}/documents?lang=en")
                    faqs_json = fetch_json(f"{BASE_URL}/{scheme_id}/faqs?lang=en")
                    
                    scheme["documents"] = normalize_documents(docs_json) if docs_json else []
                    scheme["faqs"] = normalize_faqs(faqs_json) if faqs_json else []
                
                all_schemes.append(scheme)
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching {slug}: {e}")
                continue
        
        return jsonify({
            "schemes": all_schemes,
            "total": len(all_schemes),
            "requested": len(slugs)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    """Proxy chat requests to Gemini using the backend secret key."""
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get('message') or '').strip()

        if not message:
            return jsonify({"error": "No message provided"}), 400

        reply, error = generate_gemini_reply(message)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"reply": reply})

    except requests.HTTPError as e:
        return jsonify({"error": f"Gemini request failed: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===============================
# RUN SERVER
# ===============================
if __name__ == '__main__':
    import os
    
    print("\n" + "="*60)
    print("🚀 MyScheme Backend Proxy Server")
    print("="*60)
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    print(f"Server running on port: {port}")
    print(f"Debug mode: {debug_mode}")
    print("\nEndpoints:")
    print("  GET  /health              - Health check")
    print("  GET  /api/schemes         - List all scheme slugs")
    print("  GET  /api/scheme/<slug>   - Get scheme details")
    print("  POST /api/schemes/batch   - Get multiple schemes")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)