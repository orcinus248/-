import React, { useState } from 'react';

type Event = {
  date: string;
  event: string;
  grades: string[];
  departments: string[];
  courses?: string[];
};

const events: Event[] = [
  { date: '2025-04-10', event: '入学式', grades: ['1', '2', '3', '4'], departments: ['海事', '海洋', '流通'] },
  { date: '2025-05-01', event: '海洋学科オリエンテーション', grades: ['1'], departments: ['海洋'] },
  { date: '2025-06-25', event: '海洋学科 合同校外学習', grades: ['3', '4'], departments: ['海洋'] },
  { date: '2025-10-01', event: '制御専攻 実習A', grades: ['3', '4'], departments: ['海洋'], courses: ['制御'] },
  { date: '2025-10-15', event: '機関専攻 実習B', grades: ['3', '4'], departments: ['海洋'], courses: ['機関'] },
  { date: '2025-11-01', event: '海洋学科共通講演会', grades: ['3', '4'], departments: ['海洋'] },
  { date: '2025-07-20', event: '流通学科インターンシップ説明会', grades: ['3'], departments: ['流通'] },
  // 他の行事もここに追加できます
];

const grades = ['1', '2', '3', '4'];
const departments = ['海事', '海洋', '流通'];
const courses = ['制御', '機関'];

function App() {
  const [selectedGrade, setSelectedGrade] = useState('1');
  const [selectedDept, setSelectedDept] = useState('海事');
  const [selectedCourse, setSelectedCourse] = useState('制御');

  const showCourse =
    (selectedGrade === '3' || selectedGrade === '4') && selectedDept === '海洋';

  const filteredEvents = events.filter(ev =>
    ev.grades.includes(selectedGrade) &&
    ev.departments.includes(selectedDept) &&
    (
      !showCourse
        ? true
        : (!ev.courses || ev.courses.includes(selectedCourse))
    )
  );

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <h2>学校行事予定表</h2>
      <div>
        <label>
          学年: 
          <select value={selectedGrade} onChange={e => setSelectedGrade(e.target.value)}>
            {grades.map(g => <option key={g} value={g}>{g}年</option>)}
          </select>
        </label>
        <label style={{ marginLeft: "1em" }}>
          学科: 
          <select value={selectedDept} onChange={e => setSelectedDept(e.target.value)}>
            {departments.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>
        {showCourse &&
          <label style={{ marginLeft: "1em" }}>
            コース:
            <select value={selectedCourse} onChange={e => setSelectedCourse(e.target.value)}>
              {courses.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
        }
      </div>
      <hr />
      <ul>
        {filteredEvents.length === 0 && <li>該当する行事はありません</li>}
        {filteredEvents.map(ev => (
          <li key={ev.date + ev.event}>{ev.date} {ev.event}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;