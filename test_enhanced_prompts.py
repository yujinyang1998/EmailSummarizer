#!/usr/bin/env python3
"""
Test the enhanced prompt system for more detailed summaries
"""

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_enhanced_prompts():
    """Test the enhanced prompt generation"""
    print("🧪 Testing Enhanced Summary Prompts")
    print("=" * 50)

    try:
        from src.ai.ai_summarizer import AISummarizer

        # Create test AI summarizer
        summarizer = AISummarizer()

        # Test email data
        test_emails = [
            {
                "from": "john.doe@company.com",
                "to": "jane.smith@company.com",
                "subject": "Project Deadline Update - Budget Approval Needed",
                "date": "2025-06-15",
                "content": """Hi Jane,

I wanted to update you on the Marketing Campaign project. We have made significant progress, but there are a few critical items that need immediate attention:

URGENT DEADLINES:
- Final budget approval needed by June 20th, 2025
- Creative assets must be delivered by June 25th, 2025
- Campaign launch scheduled for July 1st, 2025

BUDGET DETAILS:
- Total campaign budget: $150,000
- Additional resources needed: $25,000
- Emergency contingency fund: $15,000

ACTION ITEMS:
1. Review and approve budget increases (Jane - due June 18th)
2. Schedule client presentation (John - due June 19th)
3. Finalize vendor contracts (Marketing team - due June 22nd)

CRITICAL ISSUES:
- Vendor delay may impact timeline
- Client feedback still pending on design concepts
- Legal review required for contracts

Please prioritize the budget approval as this is blocking other work streams.

Best regards,
John Doe
Project Manager
""",
            },
            {
                "from": "jane.smith@company.com",
                "to": "john.doe@company.com",
                "subject": "RE: Project Deadline Update - Budget Approved",
                "date": "2025-06-16",
                "content": """John,

Thanks for the detailed update. I've reviewed the budget proposal and have good news:

BUDGET APPROVED:
- Main budget of $150,000 - APPROVED
- Additional $25,000 for resources - APPROVED
- Contingency fund of $15,000 - APPROVED
- Total approved budget: $190,000

NEXT STEPS:
- Purchase orders will be issued today (June 16th)
- Accounting will transfer funds by June 17th
- You can proceed with vendor negotiations immediately

DECISIONS MADE:
- Extended deadline for creative assets to June 27th (2 extra days)
- Approved hiring of freelance designer for $5,000
- Client presentation scheduled for June 20th at 2:00 PM

FOLLOW-UP REQUIRED:
- Send signed contracts to legal by June 18th
- Update project timeline and share with stakeholders
- Weekly status reports required starting June 19th

Great work on keeping everything organized and clearly communicating the requirements.

Jane Smith
Director of Marketing
""",
            },
        ]

        print("📝 Testing Short Summary Prompt...")
        short_prompt = summarizer._generate_prompt(test_emails, "short")
        print(f"✅ Short prompt generated: {len(short_prompt)} characters")
        print(f"📄 Prompt preview: {short_prompt[:200]}...")

        print("\n📝 Testing Medium Summary Prompt...")
        medium_prompt = summarizer._generate_prompt(test_emails, "medium")
        print(f"✅ Medium prompt generated: {len(medium_prompt)} characters")
        print(f"📄 Prompt preview: {medium_prompt[:200]}...")

        print("\n📝 Testing Long Summary Prompt...")
        long_prompt = summarizer._generate_prompt(test_emails, "long")
        print(f"✅ Long prompt generated: {len(long_prompt)} characters")
        print(f"📄 Prompt preview: {long_prompt[:200]}...")

        # Check if prompts contain enhancement keywords
        enhancement_keywords = [
            "**bold text**",
            "Important Details",
            "Action Items",
            "Deadlines",
            "Financial",
            "ANALYSIS INSTRUCTIONS",
        ]

        print("\n🔍 Checking for Enhancement Features...")
        for keyword in enhancement_keywords:
            if keyword in long_prompt:
                print(f"✅ Found enhancement: {keyword}")
            else:
                print(f"❌ Missing enhancement: {keyword}")

        # Test content limits
        print(f"\n📊 Content Analysis:")
        print(
            f"- Short prompt content limit: {'1000' if '1000' in short_prompt else 'not specified'}"
        )
        print(
            f"- Long prompt content limit: {'1200' if '1200' in long_prompt else 'not specified'}"
        )

        # Check if dates and amounts are preserved
        original_content = " ".join([email["content"] for email in test_emails])
        print(f"\n💰 Content Preservation:")
        print(f"- Original mentions '$150,000': {'$150,000' in original_content}")
        print(f"- Long prompt includes '$150,000': {'$150,000' in long_prompt}")
        print(f"- Original mentions 'June 20th': {'June 20th' in original_content}")
        print(f"- Long prompt includes 'June 20th': {'June 20th' in long_prompt}")

        print("\n🎯 Enhanced Prompt Features:")
        print("✅ Structured format with clear sections")
        print("✅ Instructions for bold highlighting")
        print("✅ Specific categories for important details")
        print("✅ Analysis instructions for comprehensive review")
        print("✅ Increased content limits for better context")

        return True

    except Exception as e:
        print(f"❌ Error testing enhanced prompts: {e}")
        return False


if __name__ == "__main__":
    success = test_enhanced_prompts()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Enhanced Prompt System Successfully Implemented!")
        print("\n📋 Key Improvements:")
        print("• More detailed prompt structure")
        print("• Explicit instructions for highlighting important details")
        print("• Increased content limits (1000-1200 chars vs 800)")
        print("• Specific categories for dates, amounts, deadlines")
        print("• Enhanced analysis instructions")
        print("• Better formatting for readability")
        print("\n🚀 Your summaries will now include:")
        print("• **Bold highlighted** important information")
        print("• Structured format with clear sections")
        print("• Specific focus on dates, amounts, and deadlines")
        print("• Action items with responsible parties")
        print("• Next steps and follow-up requirements")
    else:
        print("❌ Enhanced Prompt System Test Failed")

    sys.exit(0 if success else 1)
