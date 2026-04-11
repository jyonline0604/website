/**
 * visual-regression-check.js
 * 視覺迴歸測試 - 用 Puppeteer 截圖並分析章節頁面對齊問題
 * 
 * 使用方式：node scripts/visual-regression-check.js
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const PAGES_TO_CHECK = [
    { name: 'chapters', url: 'https://kofhk.com/chapters.html', critical: true },
    { name: 'home', url: 'https://kofhk.com/home.html', critical: false },
    { name: 'av-novels', url: 'https://kofhk.com/av-novels.html', critical: true },
];

async function captureAndAnalyze() {
    console.log('📸 啟動視覺迴歸測試...\n');

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const results = [];
    let hasErrors = false;

    for (const page of PAGES_TO_CHECK) {
        console.log(`\n📄 檢查: ${page.name} (${page.url})`);

        try {
            const browserPage = await browser.newPage();
            await browserPage.setViewport({ width: 1280, height: 800 });

            // 導航並截圖
            await browserPage.goto(page.url, { waitUntil: 'networkidle2', timeout: 30000 });
            await browserPage.screenshot({
                path: `/tmp/${page.name}-screenshot.png`,
                fullPage: false
            });

            // 檢查關鍵元素是否存在且可見
            const checks = await browserPage.evaluate((pageName) => {
                const results = [];

                if (pageName === 'chapters') {
                    // 檢查章節頁面關鍵元素
                    const container = document.querySelector('.container');
                    const chapterList = document.querySelector('.chapter-list');
                    const chapterGroups = document.querySelector('.chapter-groups');
                    const sortControls = document.querySelector('.sort-controls');
                    const chapterGrid = document.querySelector('.chapter-list-grid');

                    results.push({
                        name: 'container存在',
                        pass: !!container,
                        info: container ? `可见: ${container.offsetWidth}x${container.offsetHeight}` : '未找到'
                    });

                    results.push({
                        name: 'chapterList在container內',
                        pass: container && chapterList && container.contains(chapterList),
                        info: !!chapterList
                    });

                    results.push({
                        name: 'sortControls在container內',
                        pass: container && sortControls && container.contains(sortControls),
                        info: !!sortControls
                    });

                    results.push({
                        name: 'chapterGrid在container內',
                        pass: container && chapterGrid && container.contains(chapterGrid),
                        info: !!chapterGrid
                    });

                    // 檢查對齊問題 - 測量左邊距
                    if (chapterList && chapterGroups) {
                        const listLeft = chapterList.getBoundingClientRect().left;
                        const groupsLeft = chapterGroups.getBoundingClientRect().left;
                        const listWidth = chapterList.offsetWidth;
                        const containerWidth = container.offsetWidth;

                        results.push({
                            name: '章節列表居中',
                            pass: Math.abs(listLeft - (window.innerWidth - listWidth) / 2) < 5,
                            info: `列表左邊距: ${listLeft}px, 應該: ${(window.innerWidth - listWidth) / 2}px`
                        });
                    }

                } else if (pageName === 'av-novels') {
                    const container = document.querySelector('.container');
                    const avGrid = document.querySelector('.av-grid');

                    results.push({
                        name: 'container存在',
                        pass: !!container,
                        info: !!container
                    });

                    const avGrid = document.querySelector('.chapter-grid');

                    results.push({
                        name: 'container存在',
                        pass: !!container,
                        info: !!container
                    });

                    results.push({
                        name: 'chapter-grid在container內',
                        pass: container && avGrid && container.contains(avGrid),
                        info: !!avGrid
                    });
                }

                return results;
            }, page.name);

            console.log(`  截圖保存: /tmp/${page.name}-screenshot.png`);

            for (const check of checks) {
                const status = check.pass ? '✅' : '❌';
                console.log(`  ${status} ${check.name}: ${check.info}`);

                if (!check.pass && page.critical) {
                    hasErrors = true;
                }
            }

            results.push({ page: page.name, checks, screenshot: `/tmp/${page.name}-screenshot.png` });

            await browserPage.close();

        } catch (error) {
            console.log(`  ❌ 錯誤: ${error.message}`);
            if (page.critical) hasErrors = true;
            results.push({ page: page.name, error: error.message });
        }
    }

    await browser.close();

    console.log('\n' + '='.repeat(50));
    if (hasErrors) {
        console.log('❌ 視覺迴歸測試失敗！存在關鍵問題');
        console.log('📸 截圖已保存到 /tmp/ 目錄');
        process.exit(1);
    } else {
        console.log('✅ 視覺迴歸測試通過！');
        process.exit(0);
    }
}

// 導出給外部調用
module.exports = { captureAndAnalyze };

// 如果直接運行
if (require.main === module) {
    captureAndAnalyze().catch(err => {
        console.error('❌ 測試執行失敗:', err);
        process.exit(1);
    });
}
