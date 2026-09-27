# SRE Copilot - Demo Script (2-3 Minute Video)

## Video Structure

**Total Duration**: 2-3 minutes
**Target Audience**: Kiro University Final Exam Reviewers
**Format**: Screen recording with voice-over narration

---

## SEGMENT 1: Introduction (15 seconds)

### Visual
- Title slide: "SRE Copilot - AI-Assisted Incident Response"
- Subtitle: "Human-in-the-Loop Remediation for Cloud Infrastructure"

### Narration
"Welcome to SRE Copilot, an AI-assisted incident response system with mandatory human approval for all state-changing operations."

---

## SEGMENT 2: Problem & Solution (20 seconds)

### Visual
- Split screen showing:
  - Left: "Manual Incident Response" (red X)
    - Slow
    - Error-prone
    - Inconsistent
  - Right: "SRE Copilot" (green checkmark)
    - AI-powered analysis
    - Human governance
    - Complete audit trail

### Narration
"Traditional incident response is slow and inconsistent. SRE Copilot augments human operators with AI-powered root cause analysis while maintaining human authority over all production changes."

---

## SEGMENT 3: Architecture Overview (30 seconds)

### Visual
- Animated architecture diagram showing component flow
- Highlight the HITL Approval Service with a warning icon

### Narration
"The system follows a strict safety boundary. AI recommends, but humans authorize. All state-changing operations must pass through the Human-in-the-Loop approval boundary. This is a non-negotiable security requirement."

---

## SEGMENT 4: Spec-Driven Development (20 seconds)

### Visual
- Show `.kiro/specs/` directory structure
- Brief scroll through requirements.md

### Narration
"The project follows a rigorous spec-driven development methodology. All requirements, design decisions, and tasks are documented before implementation."

---

## SEGMENT 5: Steering & Hooks (20 seconds)

### Visual
- Show `.kiro/steering/` directory
- Show `.kiro/hooks/` directory

### Narration
"Steering documents guide development decisions, while hooks enforce security boundaries automatically."

---

## SEGMENT 6: Property-Based Testing (20 seconds)

### Visual
- Show `tests/` directory structure
- Run test command showing property-based tests

### Narration
"The system uses property-based testing for comprehensive validation. Hundreds of test scenarios are automatically generated and validated."

---

## SEGMENT 7: Kiro Power & MCP (20 seconds)

### Visual
- Show `sre-copilot-power/` directory
- Display MCP configuration

### Narration
"A custom Kiro Power provides AWS service integration through the Model Context Protocol."

---

## SEGMENT 8: Live Demo - APPROVE Scenario (30 seconds)

### Visual
- Terminal window: `python demo_end_to_end.py`
- Show APPROVE scenario executing all 10 steps
- Show final output: "✅ All checks passed"

### Narration
"Let's see the complete workflow. Alert received, evidence collected, AI diagnosis generated, risk assessed, human approval granted, SSM executed, health verified, incident resolved with complete audit trail."

---

## SEGMENT 9: Safety Invariant Demo (20 seconds)

### Visual
- Show SAFETY_INVARIANT scenario output
- Highlight: "SSM success ≠ Recovery verified"

### Narration
"Crucially, SSM execution success alone does NOT mark incidents as resolved. Health verification is required."

---

## SEGMENT 10: Security Validation (15 seconds)

### Visual
- Show security boundary validation output

### Narration
"All security boundaries validated. AI has zero execution permissions. All state changes require human approval."

---

## SEGMENT 11: Conclusion (10 seconds)

### Visual
- Summary slide with achievements

### Narration
"SRE Copilot demonstrates AI-assisted incident response with complete human governance. Ready for production deployment."

---

## Demo Checklist

### Pre-Recording Setup

- [ ] Clean terminal window
- [ ] Test demo script
- [ ] Verify all scenarios pass
- [ ] Prepare architecture diagram
- [ ] Test audio levels

### Recording Equipment

- [ ] Screen recording software
- [ ] Microphone
- [ ] Quiet environment

### Post-Recording

- [ ] Review entire video
- [ ] Check audio quality
- [ ] Confirm timing (2-3 minutes)

---

## Key Talking Points

1. **Architecture**: 9 components, safety boundary, security
2. **Methodology**: Spec-driven, steering, hooks, testing
3. **Implementation**: Local development, mock providers
4. **Safety**: AI cannot execute, approval required, verification required

---

## Success Criteria

✅ Explain problem and solution
✅ Demonstrate complete workflow
✅ Highlight security boundaries
✅ Show spec-driven approach
✅ Validate safety invariants
✅ Complete within time limit

---

**Document Version**: 1.0
**Last Updated**: September 26, 2026