# Railway Google Gen AI Provider Fix

## Issue
When deploying to Railway, you may encounter this error:
```
ImportError: Google Gen AI native provider not available, to install: uv add "crewai[google-genai]"
```

## Solution
The `requirements.txt` file has been updated to include the Google Gen AI provider:
```
crewai[google-genai]>=0.28.0
```

## What This Does
- Installs CrewAI with the Google Gen AI native provider
- Enables proper integration with Gemini models
- Required for using Gemini models with CrewAI

## Verification
After deployment, check the Railway logs to ensure:
1. The package installs successfully
2. No ImportError occurs when starting the application
3. The workers boot successfully

## Alternative Installation
If you need to install manually, you can use:
```bash
pip install "crewai[google-genai]>=0.28.0"
```

## Notes
- This is required for CrewAI to use Gemini models natively
- Without this, CrewAI will try to use the native provider but fail to import it
- The bracket notation `[google-genai]` installs the extra dependencies needed for Google Gen AI support

