# ELEC-392 Engineering Logbook System

> A hybrid documentation system combining markdown logbooks with GitHub Issues for comprehensive project tracking and reflection

# Overview

This repository implements a modern digital engineering logbook specifically designed for ELEC-392 course projects. It replaces traditional paper logbooks with a structured, version-controlled system that makes documentation easier for students and grading simpler for TAs.

## Why This System?
- Document technical work and decisions
- Reflect on learning and challenges
- Track time investment and progress
- Demonstrate accountability in grading

This digital system maintains all these benefits while adding:
- Version control and automatic backups
- Easy search and navigation
- Automated grading assistance
- Embedded images, equations, and code
- Seamless team collaboration

# System Architecture

This logbook uses a hybrid approach:

## 1. Markdown Files (`/logbook`)
**Purpose**: Technical documentation and detailed work logs

- Daily/session-based entries in markdown format
- YAML frontmatter for metadata (date, hours, status)
- Support for LaTeX equations, code blocks, images
- Organized by week: `logbook/week-01/`, `logbook/week-02/`, etc.
- Example: `2025-01-08_circuit-design.md`

**Best for**: 
- Circuit designs and schematics
- Calculations and analysis
- Test results and measurements
- Technical diagrams and photos
- Implementation details

## 2. GitHub Issues
**Purpose**: Reflections

- Weekly reflection issues using templates
- Track challenges, solutions, and learning
- Link to specific logbook entries
- Easy commenting and TA feedback
- Project Board integration for progress tracking

**Best for**:
- Weekly reflection summaries
- Learning outcomes and insights
- Challenge documentation
- Team discussions
- Grading submissions

## 3. Project Board
**Purpose**: Visual task management and progress tracking

- Columns: To Do, In Progress, Completed, Reflections, Status Reports
- Links issues and tasks together
- Provides overview of project status
- Required columns for grading: Reflections

## 4. Images (`/images`)

**Purpose**: Centralized storage for all project images and diagrams

- Circuit diagrams and schematics
- Oscilloscope screenshots
- PCB layouts and photos
- Test setup photos
- Data visualization plots
- Organized by week: `images/week-01/`, `images/week-02/`, etc. if needed

**Best for**:

- Visual documentation of circuits and hardware
- Test results and measurements
- Progress photos
- Diagrams and flowcharts
- Any image referenced in logbook entries

# Quick Start

## 1. Accept the GitHub Classroom Assignment (No Fork Needed)
1. Open the GitHub Classroom assignment link provided by your instructor.
2. Click 'Accept assignment'. GitHub Classroom will automatically create a repository for you (or your team) based on this template.
3. If working in teams, join or create your team as directed by Classroom.
4. Clone your generated repository locally:
   ```bash
   git clone https://github.com/<org-or-user>/<your-assignment-repo>.git
   cd <your-assignment-repo>
   ```
5. Team access is managed by Classroom; no manual forking or collaborator setup is required.

## 2. Set Up Your Project Board
1. Go to 'Projects' tab → 'Create a project'
   - In your repository's top menu, click on 'Projects'
   - Click the green "New project" button
   - Select "Board" as the template (recommended  for task tracking)
   - Name it: `ELEC-392 Logbook Board`
   - Click "Create"

2. Set up the preferred columns:
   - Click "+ Add column" for each of these:
     - **"To Do"** (tasks planned but not started)
     - **"In Progress"** (currently working on)
     - **"Completed"** (finished work)
     - **"Reflections"** (for weekly reflection issues)
   - You can drag columns to reorder them

3. Link Issues to your Project Board:
   - Open any existing Issue
   - On the right sidebar, click "Projects"
   - Select your `ELEC-392 Logbook Board`
   - Choose the appropriate column (e.g., "To Do")

## 3. Creating Daily Logbook Entries
The `logbook/.templates/` folder contains several logbook templates to suit different documentation needs:

- **`detailed_work_log_template.md`** - Comprehensive template for technical work with objectives, calculations, and results
- **`team_contributions_template.md`** - Track individual contributions when multiple team members work on the same day
- **`meeting_minutes_template.md`** - Document team meetings, decisions, and action items

** Flexibility in Documentation Style**

While we provide these templates as starting points, your logbook organization method is flexible. Teams should choose or adapt formats that work best for their workflow and project needs. The key requirements are:

- **Sufficient detail** - Entries should be thorough enough for reproduction and understanding
- **Clear organization** - Use consistent structure and naming conventions
- **Required metadata** - Include date, hours, status, and relevant tags
- **Regular updates** - Document work as it happens, not retroactively

You may:
- Use one template exclusively
- Mix templates based on activity type
- Create your own format that meets the requirements
- Adapt templates to better fit your team's style

**Option A: Using a Template (Recommended for Getting Started)**

1. Navigate to `logbook/.templates/` folder:
   - Click on the "logbook" folder in your repository
   - Click on ".templates"
   - Choose the template that best fits your needs

2. Copy the template:
   - Click the "Raw" button at the top right of the file view
   - Press **'**Ctrl+A** (Windows/Linux) or **Cmd+A** (Mac) to select all, then **Ctrl+C** (Windows/Linux) or **Cmd+C** (Mac) to copy

3. Create your entry:
   - Navigate back to the appropriate week folder (e.g., `logbook/week-01/`)
   - Click "Add file" → "Create new file"
   - Name it using the format: `YYYY-MM-DD_brief-description.md`
     - Example: `2025-01-15_circuit-testing.md`
   - Paste the template content using **Ctrl+V** (Windows/Linux) or **Cmd+V** (Mac)
   - Fill in all sections with your work details
   - Scroll down and click "Commit new file"

**Option B: Custom Entry Format**

1. In your week folder, click "Add file" → "Create new file"
2. Name: `YYYY-MM-DD_description.md`
3. Write your entry ensuring you include:
   - YAML frontmatter with date, hours, and status
   - Clear description of work performed
   - Challenges and solutions
   - References and relevant images/code

**Tips:**
- Make entries daily or after each work session
- Include screenshots or phots using: `![Description](../../images/week-XX/filename.png)`
- Reference equations: $V = IR$ (inline) or $$V = IR$$ (block)
- Link related Issues: `Closes #5` or `Related to #3`

## 4. Weekly Reflections (GitHub Issues)

1. Create a new Issue:
   - Go to the "Issues" tab in your repository in GitHub
   - Click the green "New issue" button

2. Fill out the reflection:
   - **Title**: `Week [#] Reflection`
     - Example: `Week 3 Reflection`
   - **Body**: Use this template:
```markdown
## Learning Outcomes
- What key concepts did you learn this week?
- Technical skills developed?

## Challenges Encountered
- Major obstacles faced
- How you solved them (or tried to)

## Progress Summary
- Link to your logbook entries for the week
- Completed tasks and achievements

## Questions/Help Needed
- Anything unclear?
- Areas where you need TA support?
```

3. Add labels:
   - Click "Labels" on the right sidebar
   - Select "reflection" (create it if it doesn't exist)
   - Add "week-[#]" label

4. Link to Project Board:
   - In the right sidebar, click "Projects"
   - Select your board
   - Place in "Reflections" column

5. Click "Submit new issue"

# Repository Structure

```
.
├── logbook/
│   ├── README.md                      # Logbook guidelines
│   ├── .templates/                    # Template for daily entries
│   ├── week-01/
│   │   └── 2025-01-08_example-*.md    # Example entries
│   ├── week-02/
│   ├── week-XX/
│   └── generate_activity_report.py    # activity summary automation script
├── images/                            # Store images here
└── .github/
    └── ISSUE_TEMPLATE/
        └── weekly-reflection.md       # Issue template for reflections
```

# Best Practices
**✅ DO:**
- Log work **as you do it**, not after the fact
- Include measurements, calculations, and results
- Document failures and mistakes (very important!)
- Add images of circuits, oscilloscope readings, etc.
- Use clear, descriptive file names
- Fill out ALL YAML frontmatter fields
- Create weekly reflection issues
- Commit and push regularly

**❌ DON'T:**
- Write entries retroactively days later
- Skip documenting "boring" or failed attempts
- Forget to add hours worked
- Use vague titles like "work.md" or "test.md"
- Let technical jargon replace clear explanations
- Plagiarize or fabricate entries


# Technical Features

### Markdown Capabilities

**LaTeX Equations:**
```markdown
Inline: $V = IR$
Block: $$P = \frac{V^2}{R}$$
```

**Code Blocks:**
```python
# Your embedded code here
def calculate_power(voltage, resistance):
    return (voltage ** 2) / resistance
```

**Images:**
```markdown
![Circuit Diagram](../images/week-01/circuit.png)
```

**Tables:**
```markdown
| Voltage | Current | Power |
|---------|---------|-------|
| 5V      | 100mA   | 0.5W  |
```

## Automation Scripts

**Activity Report Generator** (`generate_activity_report.py`):
- Scans all logbook entries
- Validates YAML frontmatter
- Calculates statistics (entries, hours, weeks)
- Checks for images and calculations
- Generates markdown report with grading suggestions

# FAQs

**Q: Can we write logbook entries as a team?**
A: Each team member should document their individual contributions. Use the `author` field in YAML frontmatter.

**Q: What if we forget to log something?**
A: Add it ASAP with a note explaining the delay. Don't fabricate timestamps.

**Q: How often should we create entries?**
A: Aim for **every work session**. Minimum 2-3 entries per week per person.

**Q: Can we edit old entries?**
A: Minor corrections are OK (typos, formatting). Major changes should be noted. Git tracks all edits anyway.

**Q: What about failed experiments?**
A: **Document them!** Failures are valuable learning experiences. Explain what went wrong and why.

**Q: How much detail is enough?**
A: Someone else should be able to reproduce your work from your logbook. Include all relevant numbers, equations, and decisions.

# Additional Resources

- [ELEC-392 Course GitBook](https://elec392.gitbook.io/elec-392/8Ty9Nx3l84dHok0cVgCY/) - Official course documentation and guidelines

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Issues Documentation](https://docs.github.com/en/issues)
- [LaTeX Math Symbols](https://www.overleaf.com/learn/latex/List_of_Greek_letters_and_math_symbols)
- [Engineering Logbook Best Practices](https://engineergirl.org/125/engineering-notebook)


# Getting Help

- **Technical Issues**: Ask a question in the course Piazza 
- **Grading Questions**: Contact your Project Manager (TA)
- **GitHub Problems**: Check [GitHub Docs](https://docs.github.com/) or ask in class


# License & Academic Integrity

This template is provided for ELEC-392 course use. 

**Academic Integrity Notice**: Your logbook is an individual/team assessment component. Do not share detailed technical solutions with other teams. Plagiarism will result in academic penalties.

Happy Logging! *Remember: Your logbook is not just for grades—it's a professional skill that will serve you throughout your engineering career.*