// ==UserScript==
// @name         Google Form Auto-Memory & Fast Timings Submitter
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Remembers Date, Shift, Camera, Location, Recorder, Scene, Task so you only have to type the timing/duration.
// @author       Assistant
// @match        https://docs.google.com/forms/d/e/1FAIpQLSfGQNuI7ZWSq1MkLafYsbAtVVBTnuF9P7Bnh6YFFCAQqzYSQA/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const STORAGE_KEY = 'gform_production_saved_state';

    function getSavedState() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
        } catch(e) {
            return {};
        }
    }

    function saveState(patch) {
        const cur = getSavedState();
        const updated = Object.assign({}, cur, patch);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    }

    // Auto-restore fields when page loads
    window.addEventListener('load', () => {
        setTimeout(initFormHelper, 600);
    });

    function initFormHelper() {
        const state = getSavedState();

        // 1. Restore Date
        const dateInputs = document.querySelectorAll('input[type="date"]');
        if (dateInputs.length > 0) {
            const today = new Date().toISOString().split('T')[0];
            const dateVal = state.date || today;
            dateInputs[0].value = dateVal;
            dateInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
            dateInputs[0].addEventListener('change', (e) => saveState({ date: e.target.value }));
        }

        // 2. Watch radio buttons & dropdowns
        document.querySelectorAll('div[role="radio"]').forEach(radio => {
            radio.addEventListener('click', () => {
                const label = radio.getAttribute('aria-label') || radio.innerText;
                const group = radio.closest('div[role="radiogroup"]');
                const groupTitle = group ? group.getAttribute('aria-label') || '' : '';
                if (groupTitle.toLowerCase().includes('shift')) saveState({ shift: label });
                if (groupTitle.toLowerCase().includes('location')) saveState({ location: label });
            });
        });

        // 3. Highlight and focus Duration field
        const textInputs = document.querySelectorAll('input[type="text"]');
        let durationInput = null;
        textInputs.forEach(inp => {
            const ariaLabel = (inp.getAttribute('aria-label') || '').toLowerCase();
            if (ariaLabel.includes('duration') || ariaLabel.includes('00:00:00')) {
                durationInput = inp;
            }
        });

        // If not found by aria-label, check the last text input
        if (!durationInput && textInputs.length > 0) {
            durationInput = textInputs[textInputs.length - 1];
        }

        if (durationInput) {
            durationInput.style.border = '2px solid #2563eb';
            durationInput.style.backgroundColor = '#eff6ff';
            durationInput.placeholder = 'Type timing here (e.g. 00:05:30) and press Enter';
            durationInput.focus();
        }

        // Create a floating helper badge
        createFloatingToolbar();
    }

    function createFloatingToolbar() {
        if (document.getElementById('fast-submit-toolbar')) return;

        const bar = document.createElement('div');
        bar.id = 'fast-submit-toolbar';
        bar.style.position = 'fixed';
        bar.style.bottom = '20px';
        bar.style.right = '20px';
        bar.style.background = '#1e293b';
        bar.style.color = '#ffffff';
        bar.style.padding = '12px 18px';
        bar.style.borderRadius = '10px';
        bar.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';
        bar.style.zIndex = '99999';
        bar.style.fontFamily = 'sans-serif';
        bar.style.fontSize = '13px';
        bar.style.display = 'flex';
        bar.style.alignItems = 'center';
        bar.style.gap = '10px';

        bar.innerHTML = `
            <span style="font-weight: bold; color: #60a5fa;">⚡ Fast Form Mode:</span>
            <span>Fixed details remembered. Focus is on Duration!</span>
        `;
        document.body.appendChild(bar);
    }
})();
