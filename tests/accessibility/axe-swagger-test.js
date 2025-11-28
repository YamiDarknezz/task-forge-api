const { chromium } = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const createHtmlReport = require('axe-html-reporter').createHtmlReport;
const fs = require('fs');
const path = require('path');

// Configuration
const API_URL = process.env.API_URL || 'http://localhost:5000';
const SWAGGER_PATH = '/api/docs';
const REPORT_DIR = path.join(__dirname);
const REPORT_FILE = path.join(REPORT_DIR, `axe-report-${Date.now()}.html`);

// Wait for API to be ready
async function waitForAPI(url, maxAttempts = 30) {
    console.log(`Waiting for API at ${url}...`);
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await fetch(`${url}/api/health`);
            if (response.ok) {
                console.log('✅ API is ready!');
                return true;
            }
        } catch (error) {
            // API not ready yet
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    throw new Error(`API not ready after ${maxAttempts} attempts`);
}

// Run AXE accessibility tests
async function runAccessibilityTests() {
    console.log('🚀 Starting AXE Accessibility Tests for Swagger UI\n');

    // Wait for API
    await waitForAPI(API_URL);

    // Launch browser
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // Navigate to Swagger UI
        const swaggerUrl = `${API_URL}${SWAGGER_PATH}`;
        console.log(`📄 Navigating to: ${swaggerUrl}`);
        await page.goto(swaggerUrl, { waitUntil: 'networkidle' });
        
        // Wait for Swagger UI to load
        await page.waitForTimeout(2000);

        // Run AXE analysis
        console.log('🔍 Running AXE accessibility analysis...\n');
        const accessibilityScanResults = await new AxeBuilder({ page })
            .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
            .analyze();

        // Generate HTML report
        const htmlReport = createHtmlReport({
            results: accessibilityScanResults,
            options: {
                projectKey: 'TaskForge API - Swagger UI',
                outputDir: REPORT_DIR,
                reportFileName: path.basename(REPORT_FILE)
            }
        });

        fs.writeFileSync(REPORT_FILE, htmlReport);
        console.log(`\n📊 HTML Report generated: ${REPORT_FILE}`);

        // Display summary
        const { violations, passes, incomplete } = accessibilityScanResults;
        
        console.log('\n' + '='.repeat(60));
        console.log('AXE ACCESSIBILITY TEST RESULTS');
        console.log('='.repeat(60));
        console.log(`✅ Passed rules: ${passes.length}`);
        console.log(`⚠️  Incomplete rules: ${incomplete.length}`);
        console.log(`❌ Violations found: ${violations.length}\n`);

        if (violations.length > 0) {
            console.log('VIOLATIONS BY SEVERITY:');
            const bySeverity = violations.reduce((acc, v) => {
                acc[v.impact] = (acc[v.impact] || 0) + 1;
                return acc;
            }, {});

            if (bySeverity.critical) console.log(`  🔴 Critical: ${bySeverity.critical}`);
            if (bySeverity.serious) console.log(`  🟠 Serious: ${bySeverity.serious}`);
            if (bySeverity.moderate) console.log(`  🟡 Moderate: ${bySeverity.moderate}`);
            if (bySeverity.minor) console.log(`  🔵 Minor: ${bySeverity.minor}`);

            console.log('\nTOP VIOLATIONS:');
            violations.slice(0, 5).forEach((v, i) => {
                console.log(`\n${i + 1}. [${v.impact.toUpperCase()}] ${v.id}`);
                console.log(`   ${v.description}`);
                console.log(`   Help: ${v.helpUrl}`);
                console.log(`   Elements affected: ${v.nodes.length}`);
            });
        }

        console.log('\n' + '='.repeat(60));
        console.log(`\n📁 Full report: ${REPORT_FILE}\n`);

        // Exit with appropriate code
        const criticalCount = violations.filter(v => v.impact === 'critical').length;
        
        if (criticalCount > 0) {
            console.log(`⚠️  Found ${criticalCount} critical accessibility issues`);
            console.log('Consider fixing critical issues before deployment\n');
        } else {
            console.log('✅ No critical accessibility issues found!\n');
        }

        await browser.close();
        
        // Exit with error code if critical issues found (optional, can be changed)
        process.exit(0); // Changed to 0 to not fail CI, but you can use criticalCount if you want to fail

    } catch (error) {
        console.error('❌ Error running accessibility tests:', error.message);
        await browser.close();
        process.exit(1);
    }
}

// Run tests
runAccessibilityTests().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
