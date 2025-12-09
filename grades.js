const studentList = document.getElementById('studentList');
const searchText = document.getElementById('search');
const addStudentbtn = document.getElementById('addStudent');

const API = "http://127.0.0.1:5000/grades";

let mockStudents = [
  { name: 'Natalie', grade: '90.0' },
  { name: 'Catherine', grade: '80.0' },
  { name: 'Cameryn', grade: '70.0' },
  { name: 'Gabriel', grade: '60.0' },
  { name: 'Anthony', grade: '50.0' }
];

let students = [];

function getTemplate() {
  const div = document.createElement('div');
  div.classList.add('student-item');
  div.innerHTML = `
    <div class="student-info"></div>
    <div class="actions">
      <button class="edit">Edit</button>
      <button class="delete">Delete</button>
    </div>
  `;
  return div;
}

async function loadStudents() {
  try {
    const result$ = await fetch(API);
    const data = await result$.json();

    students = Object.entries(data).map(([name, grade]) => ({
      name,
      grade: parseFloat(grade)
    }));

    initializeList();
  } catch (error) {
    console.error('Failed to load students:', error);
  }
}

function initializeList() {
  const search = searchText.value.toLocaleLowerCase();
  studentList.innerHTML = '';

  students
    .filter(student => student.name.toLocaleLowerCase().includes(search))
    .forEach((student, index) => {
      const item = getTemplate().cloneNode(true);
      const info = item.querySelector('.student-info');
      const editButton = item.querySelector('.edit');
      const deleteButton = item.querySelector('.delete');

      info.innerHTML = 
        `<span class="student-name">${student.name}</span>
        <span class="student-grade">${student.grade}</span>`;

      editButton.onclick = () => editStudent(index);
      deleteButton.onclick = () => deleteStudent(index);

      studentList.appendChild(item);
    });
}

async function addStudent() {
  const name = prompt('Enter Student Name: ');
  if (!name) return;

  const grade = prompt('Enter Student Grade: ');
  if (grade === null || grade.trim() === '') return;

  try {
    await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, grade: parseFloat(grade) })
    });
    loadStudents();
  } catch (error) {
    console.error('Failed to add student:', error);
  }
}

async function editStudent(index) {
  const student = students[index];

  const newName = prompt('Enter Student Name: ', student.name);
  if (!newName) return;

  const newGrade = prompt('Edit grade:', student.grade);
  if (newGrade === null || newGrade.trim() === '') return;

  try {
    if (newName !== student.name) {
      await fetch(getLink(student.name), {
        method: 'DELETE'
      });

      await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName, grade: parseFloat(newGrade) })
      });
    } else {
      await fetch(getLink(student.name), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grade: parseFloat(newGrade) })
      });
    }
    loadStudents();
  } catch (error) {
    console.error('Failed to edit student:', error);
  }
}

async function deleteStudent(index) {
  const student = students[index];
  if (!confirm(`Are you sure you want to delete ${student.name}?`)) return;

  try {
    await fetch(getLink(student.name), {
      method: 'DELETE'
    });
    loadStudents();
  } catch (error) {
    console.error('Failed to delete student:', error);
  }
}

function getLink(studentName) {
  return `${API}/${encodeURIComponent(studentName)}`;
}

searchText.addEventListener('input', initializeList);
loadStudents();