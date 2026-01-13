#!/usr/bin/env python3
"""
Logbook Activity Report Generator

This script analyzes student logbook repositories and generates activity reports 
for TAs and helps students evaluate their logbook activity. 
It checks for:
- Proper file structure and naming conventions
- YAML frontmatter completeness
- Entry frequency and consistency
- Technical content quality indicators
- Image usage and documentation

Usage:
    python generate_grading_report.py <repo_path> [--output report.md]

Example:
    python generate_grading_report.py ../student-repos/team-alpha --output team-alpha-report.md
"""

import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path
import argparse


class LogbookGrader:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.logbook_path = self.repo_path / "logbook"
        self.issues = []
        self.warnings = []
        self.stats = {
            "total_entries": 0,
            "total_hours": 0.0,
            "weeks_with_entries": set(),
            "entries_with_images": 0,
            "entries_with_calculations": 0,
            "avg_entry_length": 0,
        }
    
    def parse_frontmatter(self, content):
        """Extract YAML frontmatter from markdown content."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError as e:
                return None
        return None
    
    def check_file_structure(self):
        """Verify logbook directory structure."""
        if not self.logbook_path.exists():
            self.issues.append("❌ Missing logbook directory")
            return False
        
        required_files = [
            self.logbook_path / "README.md",
        ]
        
        for req_file in required_files:
            if not req_file.exists():
                self.warnings.append(f"⚠️  Missing {req_file.relative_to(self.repo_path)}")
        
        return True
    
    def analyze_entry(self, entry_path):
        """Analyze a single logbook entry."""
        with open(entry_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check frontmatter
        frontmatter = self.parse_frontmatter(content)
        if not frontmatter:
            self.warnings.append(f"⚠️  {entry_path.name}: Missing or invalid YAML frontmatter")
            return
        
        # Required fields
        required_fields = ['title', 'date', 'week', 'author', 'hours', 'status']
        missing_fields = [field for field in required_fields if field not in frontmatter]
        if missing_fields:
            self.warnings.append(
                f"⚠️  {entry_path.name}: Missing frontmatter fields: {', '.join(missing_fields)}"
            )
        
        # Update statistics
        self.stats["total_entries"] += 1
        if 'hours' in frontmatter:
            try:
                self.stats["total_hours"] += float(frontmatter['hours'])
            except (ValueError, TypeError):
                self.warnings.append(f"⚠️  {entry_path.name}: Invalid hours value")
        
        if 'week' in frontmatter:
            self.stats["weeks_with_entries"].add(frontmatter['week'])
        
        # Content analysis
        if '![' in content or '<img' in content:
            self.stats["entries_with_images"] += 1
        
        if '$$' in content or '\\[' in content or '\\(' in content:
            self.stats["entries_with_calculations"] += 1
        
        # Count words (approximate content length)
        words = len(re.findall(r'\w+', content))
        self.stats["avg_entry_length"] += words
    
    def scan_logbook(self):
        """Scan all logbook entries."""
        if not self.check_file_structure():
            return
        
        # Find all markdown files in week-* directories
        week_dirs = sorted([d for d in self.logbook_path.iterdir() 
                           if d.is_dir() and d.name.startswith('week-')])
        
        if not week_dirs:
            self.warnings.append("⚠️  No week directories found (week-01, week-02, etc.)")
            return
        
        for week_dir in week_dirs:
            md_files = list(week_dir.glob('*.md'))
            for md_file in md_files:
                if md_file.name != 'README.md':
                    self.analyze_entry(md_file)
    
    def calculate_grade_suggestions(self):
        """Provide grading suggestions based on analysis."""
        suggestions = []
        
        # Check entry frequency
        if self.stats["total_entries"] == 0:
            suggestions.append("❌ **CRITICAL**: No logbook entries found")
        elif self.stats["total_entries"] < 3:
            suggestions.append("⚠️  **LOW**: Very few entries (<3). Encourage more frequent logging.")
        
        # Check hours logged
        if self.stats["total_hours"] < 5:
            suggestions.append("⚠️  Low time investment logged. Verify with student.")
        
        # Check content quality
        if self.stats["total_entries"] > 0:
            avg_length = self.stats["avg_entry_length"] / self.stats["total_entries"]
            if avg_length < 100:
                suggestions.append("⚠️  Entries appear brief. Encourage more detailed documentation.")
        
        # Check for technical content
        if self.stats["entries_with_calculations"] == 0 and self.stats["total_entries"] > 0:
            suggestions.append("⚠️  No mathematical calculations found. Verify technical depth.")
        
        return suggestions
    
    def generate_report(self):
        """Generate a markdown grading report."""
        self.scan_logbook()
        
        if self.stats["total_entries"] > 0:
            self.stats["avg_entry_length"] /= self.stats["total_entries"]
        
        suggestions = self.calculate_grade_suggestions()
        
        report = f"""# Logbook Grading Report

**Repository:** `{self.repo_path.name}`  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## 📊 Statistics

- **Total Entries:** {self.stats['total_entries']}
- **Total Hours Logged:** {self.stats['total_hours']:.1f} hours
- **Weeks with Entries:** {len(self.stats['weeks_with_entries'])} (Weeks: {', '.join(map(str, sorted(self.stats['weeks_with_entries'])))})
- **Entries with Images:** {self.stats['entries_with_images']}
- **Entries with Calculations:** {self.stats['entries_with_calculations']}
- **Average Entry Length:** {self.stats['avg_entry_length']:.0f} words

## 🔍 Issues Found

"""
        
        if self.issues:
            for issue in self.issues:
                report += f"{issue}\n"
        else:
            report += "✅ No critical issues found\n"
        
        report += "\n## ⚠️  Warnings\n\n"
        
        if self.warnings:
            for warning in self.warnings:
                report += f"{warning}\n"
        else:
            report += "✅ No warnings\n"
        
        report += "\n## 💡 Grading Suggestions\n\n"
        
        if suggestions:
            for suggestion in suggestions:
                report += f"{suggestion}\n"
        else:
            report += "✅ Repository meets minimum standards\n"
        
        report += """\n---

## 📝 Grading Criteria Reference

### Excellent (90-100%)
- Regular entries (3+ per week)
- Detailed technical documentation with calculations
- Proper use of images/diagrams
- Complete YAML frontmatter
- Clear reflection on challenges and solutions

### Good (80-89%)
- Consistent entries (2-3 per week)
- Technical content with some calculations
- Some visual documentation
- Minor frontmatter issues

### Satisfactory (70-79%)
- Some entries (1-2 per week)
- Basic technical documentation
- Limited calculations or visuals
- Missing some frontmatter fields

### Needs Improvement (<70%)
- Infrequent or missing entries
- Minimal technical content
- Poor documentation practices
"""
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Generate grading reports for student logbook repositories'
    )
    parser.add_argument(
        'repo_path',
        help='Path to student repository'
    )
    parser.add_argument(
        '-o', '--output',
        default='grading_report.md',
        help='Output file path (default: grading_report.md)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.repo_path):
        print(f"Error: Repository path '{args.repo_path}' does not exist")
        sys.exit(1)
    
    grader = LogbookGrader(args.repo_path)
    report = grader.generate_report()
    
    # Write report
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated: {args.output}")
    print(f"\nQuick Summary:")
    print(f"  Entries: {grader.stats['total_entries']}")
    print(f"  Hours: {grader.stats['total_hours']:.1f}")
    print(f"  Issues: {len(grader.issues)}")
    print(f"  Warnings: {len(grader.warnings)}")


if __name__ == '__main__':
    main()#!/usr/bin/env python3
"""
Logbook Grading Report Generator

This script analyzes student logbook repositories and generates grading reports for TAs.
It checks for:
- Proper file structure and naming conventions
- YAML frontmatter completeness
- Entry frequency and consistency
- Technical content quality indicators
- Image usage and documentation

Usage:
    python generate_grading_report.py <repo_path> [--output report.md]

Example:
    python generate_grading_report.py ../student-repos/team-alpha --output team-alpha-report.md
"""

import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path
import argparse


class LogbookGrader:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.logbook_path = self.repo_path / "logbook"
        self.issues = []
        self.warnings = []
        self.stats = {
            "total_entries": 0,
            "total_hours": 0.0,
            "weeks_with_entries": set(),
            "entries_with_images": 0,
            "entries_with_calculations": 0,
            "avg_entry_length": 0,
        }
    
    def parse_frontmatter(self, content):
        """Extract YAML frontmatter from markdown content."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError as e:
                return None
        return None
    
    def check_file_structure(self):
        """Verify logbook directory structure."""
        if not self.logbook_path.exists():
            self.issues.append("❌ Missing logbook directory")
            return False
        
        required_files = [
            self.logbook_path / "README.md",
        ]
        
        for req_file in required_files:
            if not req_file.exists():
                self.warnings.append(f"⚠️  Missing {req_file.relative_to(self.repo_path)}")
        
        return True
    
    def analyze_entry(self, entry_path):
        """Analyze a single logbook entry."""
        with open(entry_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check frontmatter
        frontmatter = self.parse_frontmatter(content)
        if not frontmatter:
            self.warnings.append(f"⚠️  {entry_path.name}: Missing or invalid YAML frontmatter")
            return
        
        # Required fields
        required_fields = ['title', 'date', 'week', 'author', 'hours', 'status']
        missing_fields = [field for field in required_fields if field not in frontmatter]
        if missing_fields:
            self.warnings.append(
                f"⚠️  {entry_path.name}: Missing frontmatter fields: {', '.join(missing_fields)}"
            )
        
        # Update statistics
        self.stats["total_entries"] += 1
        if 'hours' in frontmatter:
            try:
                self.stats["total_hours"] += float(frontmatter['hours'])
            except (ValueError, TypeError):
                self.warnings.append(f"⚠️  {entry_path.name}: Invalid hours value")
        
        if 'week' in frontmatter:
            self.stats["weeks_with_entries"].add(frontmatter['week'])
        
        # Content analysis
        if '![' in content or '<img' in content:
            self.stats["entries_with_images"] += 1
        
        if '$$' in content or '\\[' in content or '\\(' in content:
            self.stats["entries_with_calculations"] += 1
        
        # Count words (approximate content length)
        words = len(re.findall(r'\w+', content))
        self.stats["avg_entry_length"] += words
    
    def scan_logbook(self):
        """Scan all logbook entries."""
        if not self.check_file_structure():
            return
        
        # Find all markdown files in week-* directories
        week_dirs = sorted([d for d in self.logbook_path.iterdir() 
                           if d.is_dir() and d.name.startswith('week-')])
        
        if not week_dirs:
            self.warnings.append("⚠️  No week directories found (week-01, week-02, etc.)")
            return
        
        for week_dir in week_dirs:
            md_files = list(week_dir.glob('*.md'))
            for md_file in md_files:
                if md_file.name != 'README.md':
                    self.analyze_entry(md_file)
    
    def calculate_grade_suggestions(self):
        """Provide grading suggestions based on analysis."""
        suggestions = []
        
        # Check entry frequency
        if self.stats["total_entries"] == 0:
            suggestions.append("❌ **CRITICAL**: No logbook entries found")
        elif self.stats["total_entries"] < 3:
            suggestions.append("⚠️  **LOW**: Very few entries (<3). Encourage more frequent logging.")
        
        # Check hours logged
        if self.stats["total_hours"] < 5:
            suggestions.append("⚠️  Low time investment logged. Verify with student.")
        
        # Check content quality
        if self.stats["total_entries"] > 0:
            avg_length = self.stats["avg_entry_length"] / self.stats["total_entries"]
            if avg_length < 100:
                suggestions.append("⚠️  Entries appear brief. Encourage more detailed documentation.")
        
        # Check for technical content
        if self.stats["entries_with_calculations"] == 0 and self.stats["total_entries"] > 0:
            suggestions.append("⚠️  No mathematical calculations found. Verify technical depth.")
        
        return suggestions
    
    def generate_report(self):
        """Generate a markdown grading report."""
        self.scan_logbook()
        
        if self.stats["total_entries"] > 0:
            self.stats["avg_entry_length"] /= self.stats["total_entries"]
        
        suggestions = self.calculate_grade_suggestions()
        
        report = f"""# Logbook Grading Report

**Repository:** `{self.repo_path.name}`  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## 📊 Statistics

- **Total Entries:** {self.stats['total_entries']}
- **Total Hours Logged:** {self.stats['total_hours']:.1f} hours
- **Weeks with Entries:** {len(self.stats['weeks_with_entries'])} (Weeks: {', '.join(map(str, sorted(self.stats['weeks_with_entries'])))})
- **Entries with Images:** {self.stats['entries_with_images']}
- **Entries with Calculations:** {self.stats['entries_with_calculations']}
- **Average Entry Length:** {self.stats['avg_entry_length']:.0f} words

## 🔍 Issues Found

"""
        
        if self.issues:
            for issue in self.issues:
                report += f"{issue}\n"
        else:
            report += "✅ No critical issues found\n"
        
        report += "\n## ⚠️  Warnings\n\n"
        
        if self.warnings:
            for warning in self.warnings:
                report += f"{warning}\n"
        else:
            report += "✅ No warnings\n"
        
        report += "\n## 💡 Grading Suggestions\n\n"
        
        if suggestions:
            for suggestion in suggestions:
                report += f"{suggestion}\n"
        else:
            report += "✅ Repository meets minimum standards\n"
        
        report += """\n---

## 📝 Grading Criteria Reference

### Excellent (90-100%)
- Regular entries (3+ per week)
- Detailed technical documentation with calculations
- Proper use of images/diagrams
- Complete YAML frontmatter
- Clear reflection on challenges and solutions

### Good (80-89%)
- Consistent entries (2-3 per week)
- Technical content with some calculations
- Some visual documentation
- Minor frontmatter issues

### Satisfactory (70-79%)
- Some entries (1-2 per week)
- Basic technical documentation
- Limited calculations or visuals
- Missing some frontmatter fields

### Needs Improvement (<70%)
- Infrequent or missing entries
- Minimal technical content
- Poor documentation practices
"""
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Generate grading reports for student logbook repositories'
    )
    parser.add_argument(
        'repo_path',
        help='Path to student repository'
    )
    parser.add_argument(
        '-o', '--output',
        default='grading_report.md',
        help='Output file path (default: grading_report.md)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.repo_path):
        print(f"Error: Repository path '{args.repo_path}' does not exist")
        sys.exit(1)
    
    grader = LogbookGrader(args.repo_path)
    report = grader.generate_report()
    
    # Write report
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated: {args.output}")
    print(f"\nQuick Summary:")
    print(f"  Entries: {grader.stats['total_entries']}")
    print(f"  Hours: {grader.stats['total_hours']:.1f}")
    print(f"  Issues: {len(grader.issues)}")
    print(f"  Warnings: {len(grader.warnings)}")


if __name__ == '__main__':
    main()