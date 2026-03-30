<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HTU Course Development Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #07111f;
      --panel: rgba(11, 23, 42, 0.88);
      --panel-2: rgba(16, 31, 57, 0.95);
      --line: rgba(255,255,255,0.08);
      --text: #e8eefc;
      --muted: #97a8cb;
      --accent: #7dd3fc;
      --accent-2: #a78bfa;
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #fb7185;
    }

    body {
      background:
        radial-gradient(circle at top left, rgba(125,211,252,0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(167,139,250,0.12), transparent 25%),
        linear-gradient(180deg, #030712 0%, #07111f 100%);
      color: var(--text);
      min-height: 100vh;
    }

    .glass {
      background: var(--panel);
      backdrop-filter: blur(14px);
      border: 1px solid var(--line);
      box-shadow: 0 20px 50px rgba(0,0,0,0.28);
    }

    .glass-soft {
      background: var(--panel-2);
      border: 1px solid var(--line);
      box-shadow: 0 14px 40px rgba(0,0,0,0.22);
    }

    .pill {
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.04);
    }

    .filter-select, .search-input {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.10);
      color: var(--text);
    }

    .filter-select:focus, .search-input:focus {
      outline: none;
      border-color: rgba(125,211,252,0.7);
      box-shadow: 0 0 0 3px rgba(125,211,252,0.15);
    }

    .metric-card {
      position: relative;
      overflow: hidden;
    }

    .metric-card::after {
      content: "";
      position: absolute;
      inset: auto -20% -55% auto;
      width: 140px;
      height: 140px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(125,211,252,0.18), transparent 65%);
    }

    .mini-label {
      color: var(--muted);
      font-size: 0.78rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .progress-track {
      background: rgba(255,255,255,0.07);
      border-radius: 999px;
      overflow: hidden;
      height: 9px;
    }

    .progress-bar {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }

    .table-wrap::-webkit-scrollbar { height: 10px; width: 10px; }
    .table-wrap::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 999px; }

    .status-chip {
      font-size: 0.72rem;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      border: 1px solid transparent;
      white-space: nowrap;
    }

    .status-development { background: rgba(52,211,153,0.12); color: #86efac; border-color: rgba(52,211,153,0.25); }
    .status-review { background: rgba(251,191,36,0.12); color: #fde68a; border-color: rgba(251,191,36,0.24); }
    .status-planning { background: rgba(125,211,252,0.12); color: #bae6fd; border-color: rgba(125,211,252,0.24); }
    .status-other { background: rgba(167,139,250,0.12); color: #ddd6fe; border-color: rgba(167,139,250,0.24); }

    .tab-btn.active {
      background: linear-gradient(90deg, rgba(125,211,252,0.18), rgba(167,139,250,0.16));
      color: white;
      border-color: rgba(125,211,252,0.25);
    }

    .loading-shimmer {
      background: linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.08), rgba(255,255,255,0.04));
      background-size: 200% 100%;
      animation: shimmer 1.6s infinite linear;
      border-radius: 1rem;
    }

    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }
  </style>
</head>
<body class="px-4 py-6 md:px-8 lg:px-10">
  <div class="max-w-7xl mx-auto space-y-6">
    <header class="glass rounded-3xl p-6 md:p-8">
      <div class="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
        <div class="space-y-4 max-w-3xl">
          <div class="flex flex-wrap items-center gap-2 text-sm text-sky-200">
            <span class="pill rounded-full px-3 py-1">Interactive HTML Dashboard</span>
            <span class="pill rounded-full px-3 py-1">Smart Filtering</span>
            <span class="pill rounded-full px-3 py-1">Semester • Course • Instructor</span>
          </div>
          <div>
            <h1 class="text-3xl md:text-4xl font-semibold tracking-tight">HTU Course Development Dashboard</h1>
            <p class="text-slate-300 mt-3 leading-7 max-w-2xl">
              Explore course development progress and TLC participation from one place. The dashboard automatically adapts the insights based on the selected semester, course, instructor, school, or department.
            </p>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 w-full xl:w-auto xl:min-w-[480px]" id="heroSummary">
          <div class="glass-soft rounded-2xl p-4"><div class="loading-shimmer h-16"></div></div>
          <div class="glass-soft rounded-2xl p-4"><div class="loading-shimmer h-16"></div></div>
          <div class="glass-soft rounded-2xl p-4"><div class="loading-shimmer h-16"></div></div>
          <div class="glass-soft rounded-2xl p-4"><div class="loading-shimmer h-16"></div></div>
        </div>
      </div>
    </header>

    <section class="glass rounded-3xl p-5 md:p-6 space-y-5">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold">Filters</h2>
          <p class="text-slate-400 text-sm mt-1">All filters work together. Choosing a course or instructor updates the KPIs, charts, and detail tables.</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button id="clearFiltersBtn" class="px-4 py-2 rounded-xl pill text-sm hover:bg-white/10 transition">Clear filters</button>
          <button id="exportBtn" class="px-4 py-2 rounded-xl bg-sky-400/15 border border-sky-300/20 text-sky-100 text-sm hover:bg-sky-400/20 transition">Export current table CSV</button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-4">
        <div>
          <label class="mini-label block mb-2">Semester</label>
          <select id="semesterFilter" class="filter-select w-full rounded-2xl px-4 py-3 text-sm"></select>
        </div>
        <div>
          <label class="mini-label block mb-2">School</label>
          <select id="schoolFilter" class="filter-select w-full rounded-2xl px-4 py-3 text-sm"></select>
        </div>
        <div>
          <label class="mini-label block mb-2">Department</label>
          <select id="departmentFilter" class="filter-select w-full rounded-2xl px-4 py-3 text-sm"></select>
        </div>
        <div>
          <label class="mini-label block mb-2">Course</label>
          <select id="courseFilter" class="filter-select w-full rounded-2xl px-4 py-3 text-sm"></select>
        </div>
        <div>
          <label class="mini-label block mb-2">Instructor</label>
          <select id="instructorFilter" class="filter-select w-full rounded-2xl px-4 py-3 text-sm"></select>
        </div>
        <div>
          <label class="mini-label block mb-2">Search</label>
          <input id="searchInput" class="search-input w-full rounded-2xl px-4 py-3 text-sm" placeholder="Search course, SME, PM, dept..." />
        </div>
      </div>

      <div class="flex flex-wrap gap-2" id="activeFilterChips"></div>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4" id="metricCards"></section>

    <section class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <div class="glass rounded-3xl p-5 md:p-6 xl:col-span-7 space-y-4">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h3 class="text-lg font-semibold">Progress overview</h3>
            <p class="text-sm text-slate-400">Changes based on the current filter context.</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <button class="tab-btn active px-3 py-2 rounded-xl pill text-sm transition" data-chart-view="school">By school</button>
            <button class="tab-btn px-3 py-2 rounded-xl pill text-sm transition" data-chart-view="department">By department</button>
            <button class="tab-btn px-3 py-2 rounded-xl pill text-sm transition" data-chart-view="course">Top courses</button>
          </div>
        </div>
        <div class="h-[360px]">
          <canvas id="progressChart"></canvas>
        </div>
      </div>

      <div class="glass rounded-3xl p-5 md:p-6 xl:col-span-5 space-y-4">
        <div>
          <h3 class="text-lg font-semibold">Development stage mix</h3>
          <p class="text-sm text-slate-400">Distribution of the currently visible courses.</p>
        </div>
        <div class="h-[360px]">
          <canvas id="stageChart"></canvas>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <div class="glass rounded-3xl p-5 md:p-6 xl:col-span-5 space-y-4">
        <div>
          <h3 class="text-lg font-semibold">Instructor insight</h3>
          <p class="text-sm text-slate-400">If an instructor is selected, this panel becomes instructor-specific. Otherwise it shows the top contributors in the current view.</p>
        </div>
        <div class="h-[340px]">
          <canvas id="instructorChart"></canvas>
        </div>
      </div>

      <div class="glass rounded-3xl p-5 md:p-6 xl:col-span-7 space-y-4">
        <div>
          <h3 class="text-lg font-semibold">TLC completion snapshot</h3>
          <p class="text-sm text-slate-400">Instructor training completion pulled from the TLC sheets and connected to the main data.</p>
        </div>
        <div id="tlcPanel" class="space-y-3"></div>
      </div>
    </section>

    <section class="glass rounded-3xl p-5 md:p-6 space-y-4">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h3 class="text-lg font-semibold">Detailed records</h3>
          <p class="text-sm text-slate-400">The table reflects all active filters and search terms.</p>
        </div>
        <div class="text-sm text-slate-400" id="tableCount"></div>
      </div>

      <div class="table-wrap overflow-auto rounded-2xl border border-white/10">
        <table class="min-w-full text-sm">
          <thead class="bg-white/5 sticky top-0">
            <tr class="text-left text-slate-300">
              <th class="px-4 py-3 font-medium">Semester</th>
              <th class="px-4 py-3 font-medium">School</th>
              <th class="px-4 py-3 font-medium">Department</th>
              <th class="px-4 py-3 font-medium">Course</th>
              <th class="px-4 py-3 font-medium">Stage</th>
              <th class="px-4 py-3 font-medium">PM</th>
              <th class="px-4 py-3 font-medium">SMEs</th>
              <th class="px-4 py-3 font-medium">Progress</th>
              <th class="px-4 py-3 font-medium">Completed items</th>
            </tr>
          </thead>
          <tbody id="recordsTableBody"></tbody>
        </table>
      </div>
    </section>
  </div>

  <script>
    const DATA_URL = "https://docs.google.com/spreadsheets/d/1EL31srR2r_CXmSXEjGprdWCH3HByT5HLGFlsEhImBBM/gviz/tq?tqx=out:csv&sheet=2013";
    const TLC_SHEETS = [
      "https://docs.google.com/spreadsheets/d/1y7mPQzNxkGXMKqBVEk1X_icALvotanOkL3HL885sMAY/gviz/tq?tqx=out:csv&gid=0",
      "https://docs.google.com/spreadsheets/d/1Ksh_5KUAyuE_H_rJkf0vDRvSKJxvyt2sYSzDgLwR5Nw/gviz/tq?tqx=out:csv&gid=0",
      "https://docs.google.com/spreadsheets/d/1bRHPX7vvU49A0Q_WzaKhNwhjqS9ketpEJKU64GLSIuM/gviz/tq?tqx=out:csv&gid=0",
      "https://docs.google.com/spreadsheets/d/1B5o0uBdFrR-pGT9dxStLorAgWx3XUYyN6I-yiBZlMcc/gviz/tq?tqx=out:csv&gid=0",
    ];

    const BLOCK_COLUMNS = [
      "Detailed Outline",
      ...Array.from({ length: 15 }, (_, i) => `Block ${i + 1}`)
    ];

    const state = {
      rawCourses: [],
      rawTlc: [],
      filteredCourses: [],
      selectedChartView: 'school',
      charts: {},
      filters: {
        semester: 'All',
        school: 'All',
        department: 'All',
        course: 'All',
        instructor: 'All',
        search: ''
      }
    };

    const els = {
      heroSummary: document.getElementById('heroSummary'),
      metricCards: document.getElementById('metricCards'),
      semesterFilter: document.getElementById('semesterFilter'),
      schoolFilter: document.getElementById('schoolFilter'),
      departmentFilter: document.getElementById('departmentFilter'),
      courseFilter: document.getElementById('courseFilter'),
      instructorFilter: document.getElementById('instructorFilter'),
      searchInput: document.getElementById('searchInput'),
      activeFilterChips: document.getElementById('activeFilterChips'),
      recordsTableBody: document.getElementById('recordsTableBody'),
      tableCount: document.getElementById('tableCount'),
      tlcPanel: document.getElementById('tlcPanel'),
      clearFiltersBtn: document.getElementById('clearFiltersBtn'),
      exportBtn: document.getElementById('exportBtn')
    };

    function normalizeWhitespace(value) {
      return String(value ?? '')
        .replace(/\u00A0/g, ' ')
        .replace(/[\r\n]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    }

    function cleanName(value) {
      return normalizeWhitespace(value)
        .replace(/[.,]+$/g, '')
        .replace(/\s+/g, ' ')
        .toLowerCase();
    }

    function titleCaseStage(stage) {
      const s = normalizeWhitespace(stage);
      if (!s) return 'Unknown';
      return s.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
    }

    async function fetchCsv(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Failed to fetch ${url}`);
      const text = await response.text();
      return Papa.parse(text, { header: true, skipEmptyLines: true }).data;
    }

    function splitPeople(text) {
      return normalizeWhitespace(text)
        .split(/[,/]|\sand\s|\s&\s/gi)
        .map(v => normalizeWhitespace(v))
        .filter(Boolean);
    }

    function isCompleted(value) {
      const v = normalizeWhitespace(value).toLowerCase();
      return v !== '' && v !== 'false' && v !== '0' && v !== 'nan' && v !== 'null' && v !== 'undefined';
    }

    function parseCourses(rows) {
      return rows.map((row, index) => {
        const semester = normalizeWhitespace(row['Semester']);
        const school = normalizeWhitespace(row['School']).replace(/^SBS$/i, 'SSBS');
        const department = normalizeWhitespace(row['Department']);
        const course = normalizeWhitespace(row['Course \ pathway'] || row['Course/pathway'] || row['Course']);
        const stage = titleCaseStage(row['Development Stage']);
        const pm = normalizeWhitespace(row['ID']);
        const deptHead = normalizeWhitespace(row['Dept. Head']);
        const smes = splitPeople(row['SMEs']);

        const completedItems = BLOCK_COLUMNS.filter(col => isCompleted(row[col]));
        const progressPct = Math.round((completedItems.length / BLOCK_COLUMNS.length) * 100);

        const contributors = new Set(smes.map(cleanName));
        BLOCK_COLUMNS.forEach(col => splitPeople(row[col]).forEach(name => contributors.add(cleanName(name))));

        return {
          id: `${semester}__${school}__${department}__${course}__${index}`,
          semester,
          school,
          department,
          course,
          stage,
          pm,
          deptHead,
          smes,
          completedItems,
          progressPct,
          contributors: Array.from(contributors).filter(Boolean),
          searchBlob: [semester, school, department, course, stage, pm, deptHead, smes.join(' '), ...BLOCK_COLUMNS.map(col => row[col])]
            .map(v => normalizeWhitespace(v).toLowerCase())
            .join(' | ')
        };
      }).filter(r => r.semester && r.course);
    }

    function parseTlcSheet(rows, sheetIndex) {
      if (!rows.length) return [];
      const columns = Object.keys(rows[0]);
      const instructorCol = columns.find(c => cleanName(c).includes('istructor name') || cleanName(c).includes('instructor name')) || columns[0];
      const sessionCols = columns.filter(c => c !== instructorCol);

      return rows.map(row => {
        const instructor = normalizeWhitespace(row[instructorCol]);
        const completedSessions = sessionCols.filter(col => normalizeWhitespace(row[col]).toLowerCase() === 'true');
        return {
          instructor,
          instructorKey: cleanName(instructor),
          sheetIndex,
          totalSessions: sessionCols.length,
          completedSessions,
          completionPct: sessionCols.length ? Math.round((completedSessions.length / sessionCols.length) * 100) : 0
        };
      }).filter(r => r.instructor);
    }

    function attachTlcToCourses(courses, tlcRecords) {
      const instructorToCourseMeta = new Map();

      courses.forEach(course => {
        const names = new Set();
        course.smes.forEach(name => names.add(cleanName(name)));
        course.contributors.forEach(name => names.add(cleanName(name)));

        names.forEach(name => {
          if (!name) return;
          if (!instructorToCourseMeta.has(name)) {
            instructorToCourseMeta.set(name, { schools: new Set(), departments: new Set(), courses: new Set(), semesters: new Set() });
          }
          const meta = instructorToCourseMeta.get(name);
          meta.schools.add(course.school);
          meta.departments.add(course.department);
          meta.courses.add(course.course);
          meta.semesters.add(course.semester);
        });
      });

      return tlcRecords.map(rec => {
        const meta = instructorToCourseMeta.get(rec.instructorKey);
        return {
          ...rec,
          schools: meta ? Array.from(meta.schools) : [],
          departments: meta ? Array.from(meta.departments) : [],
          linkedCourses: meta ? Array.from(meta.courses) : [],
          semesters: meta ? Array.from(meta.semesters) : []
        };
      });
    }

    function uniqueSorted(values) {
      return Array.from(new Set(values.filter(Boolean))).sort((a, b) => a.localeCompare(b));
    }

    function populateSelect(select, values, currentValue = 'All', placeholder = 'All') {
      const options = ['All', ...values];
      select.innerHTML = options.map(v => `<option value="${escapeHtml(v)}" ${v === currentValue ? 'selected' : ''}>${escapeHtml(v === 'All' ? placeholder : v)}</option>`).join('');
    }

    function escapeHtml(value) {
      return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function getAvailableOptions(baseRows) {
      const semester = uniqueSorted(baseRows.map(r => r.semester));
      const school = uniqueSorted(baseRows.map(r => r.school));
      const department = uniqueSorted(baseRows.map(r => r.department));
      const course = uniqueSorted(baseRows.map(r => r.course));

      const instructorNames = new Set();
      baseRows.forEach(row => {
        row.smes.forEach(name => instructorNames.add(name));
        row.contributors.forEach(key => {
          const pretty = state.rawTlc.find(t => t.instructorKey === key)?.instructor;
          if (pretty) instructorNames.add(pretty);
        });
      });
      state.rawTlc.forEach(t => instructorNames.add(t.instructor));

      return {
        semester,
        school,
        department,
        course,
        instructor: uniqueSorted(Array.from(instructorNames))
      };
    }

    function instructorMatches(row, selectedInstructor) {
      if (selectedInstructor === 'All') return true;
      const key = cleanName(selectedInstructor);
      return row.contributors.includes(key) || row.smes.some(name => cleanName(name) === key);
    }

    function getFilteredCourses() {
      return state.rawCourses.filter(row => {
        const { semester, school, department, course, instructor, search } = state.filters;
        const passesSearch = !search || row.searchBlob.includes(search.toLowerCase());

        return passesSearch &&
          (semester === 'All' || row.semester === semester) &&
          (school === 'All' || row.school === school) &&
          (department === 'All' || row.department === department) &&
          (course === 'All' || row.course === course) &&
          instructorMatches(row, instructor);
      });
    }

    function getFilteredTlc() {
      return state.rawTlc.filter(row => {
        const { semester, school, department, course, instructor, search } = state.filters;
        const textBlob = [row.instructor, ...row.schools, ...row.departments, ...row.linkedCourses, ...row.semesters].join(' ').toLowerCase();
        return (!search || textBlob.includes(search.toLowerCase())) &&
          (instructor === 'All' || cleanName(row.instructor) === cleanName(instructor)) &&
          (semester === 'All' || row.semesters.includes(semester)) &&
          (school === 'All' || row.schools.includes(school)) &&
          (department === 'All' || row.departments.includes(department)) &&
          (course === 'All' || row.linkedCourses.includes(course));
      });
    }

    function avg(values) {
      if (!values.length) return 0;
      return Math.round(values.reduce((a, b) => a + b, 0) / values.length);
    }

    function sumBy(rows, keyGetter, valueGetter) {
      const map = new Map();
      rows.forEach(row => {
        const key = keyGetter(row);
        const value = valueGetter(row);
        map.set(key, (map.get(key) || 0) + value);
      });
      return Array.from(map.entries());
    }

    function countBy(rows, keyGetter) {
      const map = new Map();
      rows.forEach(row => {
        const key = keyGetter(row);
        map.set(key, (map.get(key) || 0) + 1);
      });
      return Array.from(map.entries());
    }

    function renderHeroSummary(rows, tlcRows) {
      const activeInstructors = uniqueSorted(rows.flatMap(r => r.smes)).length;
      const html = [
        { label: 'Visible courses', value: rows.length },
        { label: 'Average progress', value: `${avg(rows.map(r => r.progressPct))}%` },
        { label: 'Visible instructors', value: activeInstructors },
        { label: 'Avg TLC completion', value: `${avg(tlcRows.map(r => r.completionPct))}%` }
      ].map(item => `
        <div class="glass-soft rounded-2xl p-4">
          <div class="mini-label">${escapeHtml(item.label)}</div>
          <div class="text-2xl font-semibold mt-2">${escapeHtml(item.value)}</div>
        </div>
      `).join('');
      els.heroSummary.innerHTML = html;
    }

    function renderMetricCards(rows, tlcRows) {
      const totalCompletedSlots = rows.reduce((sum, r) => sum + r.completedItems.length, 0);
      const totalPossibleSlots = rows.length * BLOCK_COLUMNS.length;
      const coverage = totalPossibleSlots ? Math.round((totalCompletedSlots / totalPossibleSlots) * 100) : 0;

      const reviewCount = rows.filter(r => r.stage.toLowerCase().includes('review')).length;
      const selectedInstructor = state.filters.instructor !== 'All' ? state.filters.instructor : null;
      const selectedCourse = state.filters.course !== 'All' ? state.filters.course : null;

      const linkedCoursesForInstructor = selectedInstructor
        ? rows.filter(r => instructorMatches(r, selectedInstructor)).length
        : null;

      const cards = [
        {
          title: 'Overall completion coverage',
          value: `${coverage}%`,
          helper: `${totalCompletedSlots} completed items out of ${totalPossibleSlots}`
        },
        {
          title: 'Courses under review',
          value: reviewCount,
          helper: reviewCount ? 'Needs follow-up and final checks' : 'No visible courses in review'
        },
        {
          title: selectedCourse ? 'Selected course progress' : 'Median-like course snapshot',
          value: selectedCourse && rows[0] ? `${rows[0].progressPct}%` : `${avg(rows.map(r => r.progressPct))}%`,
          helper: selectedCourse && rows[0] ? rows[0].course : 'Average visible course progress'
        },
        {
          title: selectedInstructor ? 'Instructor-linked courses' : 'TLC visible records',
          value: selectedInstructor ? linkedCoursesForInstructor : tlcRows.length,
          helper: selectedInstructor
            ? `Courses associated with ${selectedInstructor}`
            : 'Instructor training records in current filter'
        }
      ];

      els.metricCards.innerHTML = cards.map(card => `
        <div class="glass rounded-3xl p-5 metric-card">
          <div class="mini-label">${escapeHtml(card.title)}</div>
          <div class="text-3xl font-semibold mt-3">${escapeHtml(card.value)}</div>
          <div class="text-sm text-slate-400 mt-2 leading-6">${escapeHtml(card.helper)}</div>
        </div>
      `).join('');
    }

    function statusClass(stage) {
      const s = stage.toLowerCase();
      if (s.includes('development')) return 'status-development';
      if (s.includes('review')) return 'status-review';
      if (s.includes('planning')) return 'status-planning';
      return 'status-other';
    }

    function renderActiveFilterChips() {
      const chips = Object.entries(state.filters)
        .filter(([key, value]) => key !== 'search' ? value !== 'All' : !!value)
        .map(([key, value]) => {
          const label = key.charAt(0).toUpperCase() + key.slice(1);
          return `<span class="pill rounded-full px-3 py-1.5 text-sm">${escapeHtml(label)}: ${escapeHtml(value)}</span>`;
        });

      els.activeFilterChips.innerHTML = chips.length ? chips.join('') : '<span class="text-sm text-slate-500">No active filters</span>';
    }

    function buildProgressChartData(rows, view) {
      if (!rows.length) return { labels: [], values: [] };

      let grouped;
      if (view === 'department') {
        grouped = sumBy(rows, r => r.department, r => r.progressPct).map(([name, total]) => {
          const count = rows.filter(r => r.department === name).length;
          return [name, Math.round(total / count)];
        });
      } else if (view === 'course') {
        grouped = rows
          .map(r => [r.course, r.progressPct])
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10);
      } else {
        grouped = sumBy(rows, r => r.school, r => r.progressPct).map(([name, total]) => {
          const count = rows.filter(r => r.school === name).length;
          return [name, Math.round(total / count)];
        });
      }

      return {
        labels: grouped.map(([label]) => label),
        values: grouped.map(([, value]) => value)
      };
    }

    function renderChart(chartKey, canvasId, type, data, options = {}) {
      const ctx = document.getElementById(canvasId);
      if (state.charts[chartKey]) state.charts[chartKey].destroy();
      state.charts[chartKey] = new Chart(ctx, {
        type,
        data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#dbe7ff' } },
            tooltip: {
              backgroundColor: 'rgba(3,7,18,0.95)',
              titleColor: '#ffffff',
              bodyColor: '#dbe7ff',
              borderColor: 'rgba(255,255,255,0.08)',
              borderWidth: 1
            }
          },
          scales: type === 'doughnut' ? {} : {
            x: { ticks: { color: '#c5d3f0' }, grid: { color: 'rgba(255,255,255,0.06)' } },
            y: { beginAtZero: true, max: 100, ticks: { color: '#c5d3f0' }, grid: { color: 'rgba(255,255,255,0.06)' } }
          },
          ...options
        }
      });
    }

    function renderProgressChart(rows) {
      const { labels, values } = buildProgressChartData(rows, state.selectedChartView);
      renderChart('progressChart', 'progressChart', 'bar', {
        labels,
        datasets: [{
          label: 'Progress %',
          data: values,
          backgroundColor: ['rgba(125,211,252,0.75)', 'rgba(167,139,250,0.75)', 'rgba(52,211,153,0.75)', 'rgba(251,191,36,0.75)', 'rgba(244,114,182,0.75)', 'rgba(96,165,250,0.75)', 'rgba(74,222,128,0.75)', 'rgba(192,132,252,0.75)', 'rgba(250,204,21,0.75)', 'rgba(45,212,191,0.75)'],
          borderRadius: 10,
          borderSkipped: false
        }]
      }, {
        plugins: {
          legend: { display: false }
        }
      });
    }

    function renderStageChart(rows) {
      const grouped = countBy(rows, r => r.stage);
      renderChart('stageChart', 'stageChart', 'doughnut', {
        labels: grouped.map(([label]) => label),
        datasets: [{
          data: grouped.map(([, value]) => value),
          backgroundColor: [
            'rgba(52,211,153,0.8)',
            'rgba(251,191,36,0.8)',
            'rgba(125,211,252,0.8)',
            'rgba(167,139,250,0.8)',
            'rgba(244,114,182,0.8)'
          ],
          borderColor: 'rgba(7,17,31,1)',
          borderWidth: 2
        }]
      });
    }

    function computeInstructorData(rows, tlcRows) {
      const selectedInstructor = state.filters.instructor;

      if (selectedInstructor !== 'All') {
        const relevantCourses = rows.filter(r => instructorMatches(r, selectedInstructor));
        const tlc = tlcRows.find(t => cleanName(t.instructor) === cleanName(selectedInstructor));

        return {
          labels: relevantCourses.map(r => r.course).slice(0, 10),
          values: relevantCourses.map(r => r.progressPct).slice(0, 10),
          title: tlc ? `${selectedInstructor} • TLC ${tlc.completionPct}%` : `${selectedInstructor} • course links`
        };
      }

      const map = new Map();
      rows.forEach(row => {
        row.smes.forEach(name => {
          const key = name;
          if (!map.has(key)) map.set(key, { courses: 0, progressTotal: 0 });
          map.get(key).courses += 1;
          map.get(key).progressTotal += row.progressPct;
        });
      });

      const top = Array.from(map.entries())
        .map(([name, v]) => [name, Math.round(v.progressTotal / v.courses), v.courses])
        .sort((a, b) => b[2] - a[2])
        .slice(0, 10);

      return {
        labels: top.map(([name]) => name),
        values: top.map(([, progress]) => progress),
        title: 'Top visible instructors by linked course contribution'
      };
    }

    function renderInstructorChart(rows, tlcRows) {
      const { labels, values, title } = computeInstructorData(rows, tlcRows);
      renderChart('instructorChart', 'instructorChart', 'bar', {
        labels,
        datasets: [{
          label: title,
          data: values,
          backgroundColor: 'rgba(167,139,250,0.78)',
          borderRadius: 10,
          borderSkipped: false
        }]
      }, {
        indexAxis: 'y',
        plugins: { legend: { display: false } }
      });
    }

    function renderTlcPanel(tlcRows, courses) {
      if (!tlcRows.length) {
        els.tlcPanel.innerHTML = '<div class="rounded-2xl border border-white/10 p-4 text-slate-400">No TLC records match the current filters.</div>';
        return;
      }

      const selectedInstructor = state.filters.instructor;

      if (selectedInstructor !== 'All') {
        const rec = tlcRows.find(t => cleanName(t.instructor) === cleanName(selectedInstructor));
        if (!rec) {
          els.tlcPanel.innerHTML = `<div class="rounded-2xl border border-white/10 p-4 text-slate-400">${escapeHtml(selectedInstructor)} has no linked TLC record in the current view.</div>`;
          return;
        }

        els.tlcPanel.innerHTML = `
          <div class="glass-soft rounded-2xl p-5 space-y-4">
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
              <div>
                <div class="text-xl font-semibold">${escapeHtml(rec.instructor)}</div>
                <div class="text-sm text-slate-400 mt-1">${escapeHtml(rec.linkedCourses.join(' • ') || 'No linked courses found')}</div>
              </div>
              <div class="text-right">
                <div class="mini-label">TLC completion</div>
                <div class="text-3xl font-semibold mt-1">${rec.completionPct}%</div>
              </div>
            </div>
            <div>
              <div class="progress-track"><div class="progress-bar" style="width:${rec.completionPct}%"></div></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div class="rounded-2xl border border-white/10 p-4">
                <div class="mini-label mb-2">Completed sessions</div>
                <div class="text-slate-200 leading-7">${rec.completedSessions.length ? rec.completedSessions.map(s => escapeHtml(s)).join('<br>') : 'No completed sessions marked'}</div>
              </div>
              <div class="rounded-2xl border border-white/10 p-4">
                <div class="mini-label mb-2">Linked semesters</div>
                <div class="text-slate-200 leading-7">${rec.semesters.length ? rec.semesters.map(s => escapeHtml(s)).join('<br>') : 'Not matched to a semester'}</div>
              </div>
            </div>
          </div>
        `;
        return;
      }

      const top = [...tlcRows].sort((a, b) => b.completionPct - a.completionPct).slice(0, 8);
      els.tlcPanel.innerHTML = top.map(rec => `
        <div class="glass-soft rounded-2xl p-4">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div>
              <div class="font-medium text-white">${escapeHtml(rec.instructor)}</div>
              <div class="text-sm text-slate-400 mt-1">${escapeHtml((rec.linkedCourses || []).slice(0, 2).join(' • ') || 'No linked course found')}</div>
            </div>
            <div class="text-sm text-slate-200 min-w-[90px] md:text-right">${rec.completionPct}%</div>
          </div>
          <div class="progress-track mt-3"><div class="progress-bar" style="width:${rec.completionPct}%"></div></div>
        </div>
      `).join('');
    }

    function renderTable(rows) {
      els.tableCount.textContent = `${rows.length} record${rows.length === 1 ? '' : 's'} shown`;

      if (!rows.length) {
        els.recordsTableBody.innerHTML = `
          <tr>
            <td colspan="9" class="px-4 py-10 text-center text-slate-400">No records match the current filters.</td>
          </tr>
        `;
        return;
      }

      els.recordsTableBody.innerHTML = rows.map(row => `
        <tr class="border-t border-white/8 hover:bg-white/5 transition">
          <td class="px-4 py-4 align-top">${escapeHtml(row.semester)}</td>
          <td class="px-4 py-4 align-top">${escapeHtml(row.school)}</td>
          <td class="px-4 py-4 align-top">${escapeHtml(row.department)}</td>
          <td class="px-4 py-4 align-top">
            <div class="font-medium text-white">${escapeHtml(row.course)}</div>
            <div class="text-xs text-slate-400 mt-1">Dept head: ${escapeHtml(row.deptHead || '—')}</div>
          </td>
          <td class="px-4 py-4 align-top"><span class="status-chip ${statusClass(row.stage)}">${escapeHtml(row.stage)}</span></td>
          <td class="px-4 py-4 align-top">${escapeHtml(row.pm || '—')}</td>
          <td class="px-4 py-4 align-top max-w-[280px]">${escapeHtml(row.smes.join(', ') || '—')}</td>
          <td class="px-4 py-4 align-top min-w-[180px]">
            <div class="flex items-center justify-between text-xs text-slate-300 mb-2">
              <span>${row.progressPct}%</span>
              <span>${row.completedItems.length}/${BLOCK_COLUMNS.length}</span>
            </div>
            <div class="progress-track"><div class="progress-bar" style="width:${row.progressPct}%"></div></div>
          </td>
          <td class="px-4 py-4 align-top text-slate-300 max-w-[320px]">${escapeHtml(row.completedItems.join(', ') || '—')}</td>
        </tr>
      `).join('');
    }

    function refreshFilterOptions() {
      const baseRows = state.rawCourses.filter(row => {
        const { semester, school, department, course, instructor, search } = state.filters;
        return (!search || row.searchBlob.includes(search.toLowerCase())) &&
          (semester === 'All' || row.semester === semester) &&
          (school === 'All' || row.school === school) &&
          (department === 'All' || row.department === department) &&
          (course === 'All' || row.course === course) &&
          instructorMatches(row, instructor);
      });

      const options = getAvailableOptions(baseRows.length ? baseRows : state.rawCourses);
      populateSelect(els.semesterFilter, options.semester, state.filters.semester, 'All semesters');
      populateSelect(els.schoolFilter, options.school, state.filters.school, 'All schools');
      populateSelect(els.departmentFilter, options.department, state.filters.department, 'All departments');
      populateSelect(els.courseFilter, options.course, state.filters.course, 'All courses');
      populateSelect(els.instructorFilter, options.instructor, state.filters.instructor, 'All instructors');
    }

    function updateDashboard() {
      const filteredCourses = getFilteredCourses();
      const filteredTlc = getFilteredTlc();
      state.filteredCourses = filteredCourses;

      renderHeroSummary(filteredCourses, filteredTlc);
      renderMetricCards(filteredCourses, filteredTlc);
      renderActiveFilterChips();
      renderProgressChart(filteredCourses);
      renderStageChart(filteredCourses);
      renderInstructorChart(filteredCourses, filteredTlc);
      renderTlcPanel(filteredTlc, filteredCourses);
      renderTable(filteredCourses);
    }

    function bindEvents() {
      els.semesterFilter.addEventListener('change', e => { state.filters.semester = e.target.value; refreshFilterOptions(); updateDashboard(); });
      els.schoolFilter.addEventListener('change', e => { state.filters.school = e.target.value; refreshFilterOptions(); updateDashboard(); });
      els.departmentFilter.addEventListener('change', e => { state.filters.department = e.target.value; refreshFilterOptions(); updateDashboard(); });
      els.courseFilter.addEventListener('change', e => { state.filters.course = e.target.value; refreshFilterOptions(); updateDashboard(); });
      els.instructorFilter.addEventListener('change', e => { state.filters.instructor = e.target.value; refreshFilterOptions(); updateDashboard(); });
      els.searchInput.addEventListener('input', e => { state.filters.search = e.target.value.trim(); refreshFilterOptions(); updateDashboard(); });

      els.clearFiltersBtn.addEventListener('click', () => {
        state.filters = { semester: 'All', school: 'All', department: 'All', course: 'All', instructor: 'All', search: '' };
        els.searchInput.value = '';
        refreshFilterOptions();
        updateDashboard();
      });

      document.querySelectorAll('[data-chart-view]').forEach(btn => {
        btn.addEventListener('click', () => {
          document.querySelectorAll('[data-chart-view]').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          state.selectedChartView = btn.dataset.chartView;
          renderProgressChart(state.filteredCourses);
        });
      });

      els.exportBtn.addEventListener('click', () => {
        if (!state.filteredCourses.length) return;
        const rows = state.filteredCourses.map(row => ({
          Semester: row.semester,
          School: row.school,
          Department: row.department,
          Course: row.course,
          Stage: row.stage,
          PM: row.pm,
          SMEs: row.smes.join(', '),
          ProgressPct: row.progressPct,
          CompletedItems: row.completedItems.join(', ')
        }));
        const csv = Papa.unparse(rows);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'htu_dashboard_filtered_data.csv';
        a.click();
        URL.revokeObjectURL(url);
      });
    }

    async function init() {
      try {
        const [mainRows, ...tlcSheetsRows] = await Promise.all([
          fetchCsv(DATA_URL),
          ...TLC_SHEETS.map(fetchCsv)
        ]);

        const parsedCourses = parseCourses(mainRows);
        const parsedTlc = tlcSheetsRows.flatMap((rows, idx) => parseTlcSheet(rows, idx));
        const matchedTlc = attachTlcToCourses(parsedCourses, parsedTlc);

        state.rawCourses = parsedCourses;
        state.rawTlc = matchedTlc;

        refreshFilterOptions();
        updateDashboard();
        bindEvents();
      } catch (error) {
        console.error(error);
        document.body.innerHTML = `
          <div class="min-h-screen flex items-center justify-center p-8">
            <div class="glass rounded-3xl p-8 max-w-2xl w-full text-center">
              <h1 class="text-2xl font-semibold mb-3">Failed to load dashboard data</h1>
              <p class="text-slate-300 leading-7">The HTML loaded, but the sheet data could not be fetched. Please verify that the Google Sheets CSV links are public and accessible.</p>
              <p class="text-sm text-rose-300 mt-4">${escapeHtml(error.message)}</p>
            </div>
          </div>
        `;
      }
    }

    init();
  </script>
</body>
</html>
