# Email Categorization with OpenAI

## Implementation Summary

### Backend Changes

1. **Email Categorizer Service** (`backend/app/services/email_categorizer.py`):
   - Uses OpenAI GPT-3.5-turbo with existing proxy setup
   - Analyzes email subject, sender, and preview text
   - Matches emails to existing user categories
   - Returns category ID or null if no good match

2. **Auto-Categorization** (`backend/app/services/email_service.py`):
   - Automatically categorizes emails after fetching from Gmail
   - Runs during login email sync process

3. **Manual Categorization API** (`backend/app/routers/emails.py`):
   - `POST /emails/categorize` - Manual AI categorization endpoint
   - Processes up to 50 uncategorized emails at once

### Frontend Changes

1. **Dashboard AI Button** (`frontend/src/app/dashboard/page.tsx`):
   - "🤖 AI Categorize" button in categories section
   - Calls categorization API and shows results
   - Refreshes category counts after categorization

2. **API Integration** (`frontend/src/lib/api.ts`):
   - Added `categorizeEmails()` function

### How It Works

#### Categorization Process:
1. **Input**: Email subject, sender name/email, body preview
2. **AI Analysis**: OpenAI analyzes content against available categories
3. **Matching**: Returns best matching category ID or null
4. **Update**: Email category_id field updated in database

#### Category Matching Logic:
- **Work**: Professional emails, project updates, work-related content
- **Personal**: Friends, family, personal communications  
- **Newsletters**: Subscription emails, newsletters
- **Promotions**: Marketing, sales, promotional content
- **Social**: Social media notifications, social platforms

#### Proxy Setup:
- Uses existing SOCKS5 proxy: `socks5://14ac63464dbca:b9e059af46@64.84.118.137:12324`
- OpenAI client configured with httpx proxy client
- Same setup as existing agent service

### Usage

#### Automatic (on login):
1. User logs in with Google OAuth
2. System fetches emails from Gmail
3. AI automatically categorizes new emails
4. Categories show updated email counts

#### Manual:
1. Click "🤖 AI Categorize" button on dashboard
2. System processes uncategorized emails
3. Shows success message with count
4. Category counts refresh automatically

### Testing

```bash
# Test categorization
cd main
python test_categorization.py

# Check results in dashboard
# - Login at http://localhost:3000
# - Click "🤖 AI Categorize" button
# - View categorized emails in categories
```

### Example Categorization:

```
Email: "Project Update: Q4 Planning" from "sarah@company.com"
→ Category: Work

Email: "Weekly Newsletter" from "newsletter@techcrunch.com"  
→ Category: Newsletters

Email: "50% Off Sale!" from "sales@store.com"
→ Category: Promotions
```

The system now automatically sorts emails using AI, making email management much more efficient and organized.