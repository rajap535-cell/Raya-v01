async function loadAnalytics() {

    const res = await fetch("http://127.0.0.1:8000/analytics/1");
    const data = await res.json();

    console.log(data);

    document.getElementById("avgSleep").innerText =
        data.reality?.sleep ?? "--";

    document.getElementById("totalSteps").innerText =
        data.reality?.steps ?? "--";

    document.getElementById("avgScreen").innerText =
        data.reality?.screen ?? "--";

    document.getElementById("avgMood").innerText =
        data.reality?.mood ?? "--";

    document.getElementById("avgStress").innerText =
        data.reality?.stress ?? "--";

    document.getElementById("avgWater").innerText =
        data.reality?.water ?? "--";

    document.getElementById("avgCalories").innerText =
        data.reality?.calories ?? "--";

    document.getElementById("avgExercise").innerText =
        data.reality?.exercise ?? "--";

    document.getElementById("avgLearning").innerText =
        data.reality?.learning ?? "--";


    const coachList = document.getElementById("coach");

    coachList.innerHTML = "";

    if (data.coach) {

        data.coach.forEach(msg => {

            const li = document.createElement("li");

            li.innerText = msg;

            coachList.appendChild(li);

        });
    }
}

async function loadLogs() {

    const res = await fetch("http://127.0.0.1:8000/logs/1");

    const logs = await res.json();

    console.log(logs);

    const table = document.getElementById("logTable");

    table.innerHTML = "";

    logs.forEach(log => {

        const row = `
            <tr>
                <td>${log.date ?? "--"}</td>
                <td>${log.steps ?? "--"}</td>
                <td>${log.sleep_hours ?? "--"}</td>
                <td>${log.work_hours ?? "--"}</td>
                <td>${log.screen_time ?? "--"}</td>
                <td>${log.mood ?? "--"}</td>
                <td>${log.stress_level ?? "--"}</td>
                <td>${log.water_intake ?? "--"}</td>
                <td>${log.calories_intake ?? "--"}</td>
                <td>${log.exercise_minutes ?? "--"}</td>
                <td>${log.learning_hours ?? "--"}</td>
            </tr>
        `;

        table.innerHTML += row;
    });
}

loadAnalytics();
loadLogs();