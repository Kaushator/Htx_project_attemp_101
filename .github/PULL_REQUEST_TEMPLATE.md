## 📋 Pull Request Description

<!-- Provide a clear and concise description of what this PR does -->

### 🎯 Type of Change

<!-- Mark the relevant option with an "x" -->
- [ ] 🐛 **Bug fix** (non-breaking change which fixes an issue)
- [ ] ✨ **New feature** (non-breaking change which adds functionality)
- [ ] 💥 **Breaking change** (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 **Documentation** (changes to documentation only)
- [ ] 🎨 **Style** (formatting, missing semi colons, etc; no production code change)
- [ ] ♻️ **Refactoring** (refactoring production code, eg. renaming a variable)
- [ ] ⚡ **Performance** (changes that improve performance)
- [ ] 🧪 **Test** (adding missing tests, refactoring tests; no production code change)
- [ ] 🔧 **Chore** (updating grunt tasks etc; no production code change)
- [ ] 🔒 **Security** (changes that improve security)

### 🔗 Related Issues

<!-- Link to the issue(s) this PR addresses -->
- Fixes #(issue number)
- Closes #(issue number)
- Related to #(issue number)

### 📝 Changes Made

<!-- Describe the changes in detail -->

#### Backend Changes
- [ ] API endpoint changes
- [ ] Database schema changes
- [ ] Service layer modifications
- [ ] Configuration updates
- [ ] External integration changes

#### Frontend Changes
- [ ] UI component updates
- [ ] State management changes
- [ ] API integration updates
- [ ] Styling changes
- [ ] User experience improvements

#### Infrastructure Changes
- [ ] Docker configuration
- [ ] CI/CD pipeline updates
- [ ] Deployment scripts
- [ ] Environment configuration

### 🧪 How Has This Been Tested?

<!-- Describe the tests you ran to verify your changes -->

#### Test Environment
- **OS**: [e.g., Ubuntu 22.04]
- **Python Version**: [e.g., 3.10.2]
- **Node.js Version**: [e.g., 18.18.0]
- **Database**: [e.g., SQLite, PostgreSQL]
- **Browser** (if frontend): [e.g., Chrome 118]

#### Test Cases
- [ ] **Unit tests**: All existing tests pass
- [ ] **Integration tests**: New/modified functionality tested
- [ ] **Manual testing**: Functionality verified manually
- [ ] **Performance testing**: No significant performance regression
- [ ] **Security testing**: No new security vulnerabilities introduced

#### Test Results
```
Paste test output or describe manual testing results
```

### 📸 Screenshots (if applicable)

<!-- Add screenshots to help explain your changes -->

#### Before
<!-- Screenshot of the current state -->

#### After
<!-- Screenshot of the new state -->

### 💔 Breaking Changes

<!-- If this is a breaking change, describe what breaks and how to migrate -->

#### What Breaks
- [ ] API endpoints
- [ ] Database schema
- [ ] Configuration format
- [ ] Function signatures
- [ ] UI components

#### Migration Guide
```bash
# Provide migration steps for users
```

### 📚 Documentation Updates

<!-- Mark what documentation has been updated -->
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] README.md updated
- [ ] DEVELOPMENT.md updated
- [ ] ARCHITECTURE.md updated
- [ ] CHANGELOG.md updated
- [ ] No documentation updates needed

### 🔒 Security Considerations

<!-- Address any security implications -->
- [ ] **Input validation**: All inputs are properly validated
- [ ] **Authentication**: Authentication requirements met
- [ ] **Authorization**: Access controls properly implemented
- [ ] **Data protection**: Sensitive data properly handled
- [ ] **Dependencies**: New dependencies security reviewed
- [ ] **No security impact**: This change doesn't affect security

### ⚡ Performance Impact

<!-- Describe the performance impact of your changes -->
- [ ] **Performance improvement**: Faster execution/response times
- [ ] **No performance impact**: Performance remains the same
- [ ] **Minor performance impact**: Small acceptable decrease
- [ ] **Performance testing required**: Needs performance review

#### Performance Metrics
<!-- If applicable, provide before/after metrics -->
```
Response time: Before X ms -> After Y ms
Memory usage: Before X MB -> After Y MB
Database queries: Before X -> After Y
```

### 📦 Dependencies

<!-- List any new dependencies added -->

#### New Dependencies
- [ ] **Backend**: New Python packages added
- [ ] **Frontend**: New npm packages added
- [ ] **Development**: New dev dependencies added
- [ ] **No new dependencies**

#### Dependency Changes
```
# List new dependencies and their purpose
package-name==version  # Purpose/reason for adding
```

### 🎯 Checklist

<!-- Ensure all items are completed before requesting review -->

#### Code Quality
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

#### Git Hygiene
- [ ] I have used conventional commit messages
- [ ] My commits are atomic and focused
- [ ] I have squashed unnecessary commits
- [ ] My branch is up to date with the target branch

#### Testing
- [ ] I have tested my changes locally
- [ ] All existing tests pass
- [ ] I have added appropriate test cases
- [ ] Test coverage is maintained or improved

#### Documentation
- [ ] Code is self-documenting or properly commented
- [ ] Public APIs are documented
- [ ] README is updated if needed
- [ ] Breaking changes are documented

### 👥 Reviewers

<!-- Tag specific reviewers if needed -->
@reviewer1 @reviewer2

### 📝 Additional Notes

<!-- Add any additional context, concerns, or notes for reviewers -->

#### Implementation Notes
<!-- Explain any complex implementation decisions -->

#### Future Improvements
<!-- Note any future improvements that could be made -->

#### Known Issues
<!-- List any known issues or limitations -->

---

### 📋 For Reviewers

#### Review Checklist
- [ ] Code quality and style
- [ ] Test coverage and quality
- [ ] Documentation completeness
- [ ] Security considerations
- [ ] Performance impact
- [ ] Breaking changes properly handled
- [ ] API design consistency
- [ ] Error handling appropriateness

#### Approval Criteria
- [ ] All CI checks pass
- [ ] Code review approved
- [ ] Documentation review completed
- [ ] Security review completed (if applicable)
- [ ] Performance review completed (if applicable)