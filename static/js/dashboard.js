(function () {
  "use strict";
  var tokenKey = "empovision_api_token";
  var token = sessionStorage.getItem(tokenKey);
  var employees = [];
  var departments = [];
  var $ = function (id) { return document.getElementById(id); };

  function api(path, options) {
    options = options || {};
    options.headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
    if (token) options.headers.Authorization = "Token " + token;
    return fetch(path, options).then(function (response) {
      return response.text().then(function (body) {
        var data = body ? JSON.parse(body) : {};
        if (!response.ok) {
          if (response.status === 401) {
            token = null;
            sessionStorage.removeItem(tokenKey);
            updateProfile();
          }
          throw new Error(typeof data === "object" ? JSON.stringify(data) : String(data));
        }
        return data;
      });
    });
  }

  function updateProfile() {
    $("profile-name").textContent = token ? "Authenticated session" : "Guest session";
    $("profile-role").textContent = token ? "Employee workspace access" : "Sign in to manage data";
    $("api-status").textContent = token ? "Connected" : "Guest";
    $("api-status-note").textContent = token ? "Authenticated API session" : "Authentication required";
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function unwrap(data) { return Array.isArray(data) ? data : (data.results || []); }
  function initials(p) { return ((p.first_name || "?").charAt(0) + (p.last_name || "").charAt(0)).toUpperCase(); }

  function renderEmployees(list) {
    $("employee-count").textContent = list.length + " records";
    if (!list.length) {
      $("employee-rows").innerHTML = '<tr><td colspan="4" class="empty-state">No employees match this search.</td></tr>';
      return;
    }
    $("employee-rows").innerHTML = list.map(function (p) {
      var name = [p.first_name, p.last_name].filter(Boolean).join(" ");
      return '<tr><td><div class="person-cell"><span class="person-avatar">' + escapeHtml(initials(p)) +
        '</span><div><div class="person-name">' + escapeHtml(name) + '</div><div class="person-email">' +
        escapeHtml(p.email) + '</div></div></div></td><td><span class="role-pill">' +
        escapeHtml(p.position) + '</span></td><td>' + escapeHtml(p.department ? p.department.name : "Unassigned") +
        '</td><td>' + escapeHtml(p.hire_date) + '</td></tr>';
    }).join("");
  }

  function renderDepartments(list) {
    $("total-departments").textContent = list.length;
    $("department-list").innerHTML = list.length ? list.map(function (d) {
      var count = employees.filter(function (p) { return p.department && p.department.id === d.id; }).length;
      return '<div class="department-item"><div class="department-line"><span class="department-name">' +
        escapeHtml(d.name) + '</span><span class="department-count">' + count +
        ' people</span></div><div class="department-location">' + escapeHtml(d.location || "Location not set") +
        '</div></div>';
    }).join("") : '<div class="empty-state">No departments found.</div>';
    $("employee-department").innerHTML = '<option value="">Unassigned</option>' + list.map(function (d) {
      return '<option value="' + Number(d.id) + '">' + escapeHtml(d.name) + '</option>';
    }).join("");
  }

  function renderAttendance(list) {
    var total = list.reduce(function (sum, r) { return sum + r.present + r.absent + r.late + r.on_leave; }, 0);
    $("attendance-total").textContent = total.toLocaleString();
    if (!list.length) {
      $("attendance-bars").innerHTML = '<div class="empty-state">No attendance records yet.</div>';
      return;
    }
    var max = Math.max.apply(null, list.map(function (r) { return r.present + r.absent + r.late + r.on_leave; }).concat([1]));
    $("attendance-bars").innerHTML = list.slice(-6).map(function (r) {
      var month = new Date(Number(r.date__year), Number(r.date__month) - 1, 1).toLocaleString("en", { month: "short" });
      return '<div class="bar-group"><div class="bar-stack"><span class="bar" title="Present: ' + r.present +
        '" style="height:' + Math.max(3, r.present / max * 66) + 'px"></span><span class="bar absent" title="Absent: ' +
        r.absent + '" style="height:' + Math.max(3, r.absent / max * 66) + 'px"></span></div><span class="bar-label">' +
        month + '</span></div>';
    }).join("");
  }

  function loadPublicData() {
    return api("/api/departments/").then(function (data) {
      departments = unwrap(data);
      renderDepartments(departments);
    }).catch(function () {
      $("department-list").innerHTML = '<div class="empty-state">Department service is unavailable.</div>';
      $("total-departments").textContent = "—";
    });
  }

  function loadPrivateData() {
    if (!token) {
      employees = [];
      $("total-employees").textContent = "—";
      $("average-salary").textContent = "—";
      $("employee-rows").innerHTML = '<tr><td colspan="4" class="empty-state">Sign in to load employee records.</td></tr>';
      $("employee-count").textContent = "Authentication required";
      $("attendance-bars").innerHTML = '<div class="empty-state">Sign in to load attendance analytics.</div>';
      $("attendance-total").textContent = "—";
      return Promise.resolve();
    }
    return Promise.all([api("/api/employees/"), api("/api/employees/stats/"), api("/api/attendance/monthly_summary/")])
      .then(function (result) {
        employees = unwrap(result[0]);
        $("total-employees").textContent = Number(result[1].total_employees || 0).toLocaleString();
        $("average-salary").textContent = result[1].avg_salary == null ? "—" :
          "₹" + Math.round(Number(result[1].avg_salary)).toLocaleString("en-IN");
        renderEmployees(employees);
        renderDepartments(departments);
        renderAttendance(result[2]);
        updateProfile();
      }).catch(function (error) {
        $("api-status").textContent = "Error";
        $("api-status-note").textContent = "Check your session and API";
        if (/401|403/.test(error.message)) $("login-dialog").showModal();
        else console.error("EmpoVision API:", error);
      });
  }

  function refresh() {
    $("today-label").textContent = new Date().toLocaleDateString("en-IN",
      { weekday: "short", day: "numeric", month: "short", year: "numeric" });
    updateProfile();
    return loadPublicData().then(loadPrivateData);
  }

  $("login-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var formElement = event.currentTarget;
    var form = new FormData(formElement);
    $("login-error").textContent = "Signing in…";
    fetch("/api-token-auth/", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: form.get("username"), password: form.get("password") })
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok || !data.token) throw new Error(data.non_field_errors ? data.non_field_errors.join(" ") : "Invalid username or password.");
        token = data.token;
        sessionStorage.setItem(tokenKey, token);
        $("login-dialog").close();
        formElement.reset();
        return refresh();
      });
    }).catch(function (error) { $("login-error").textContent = error.message; });
  });

  $("logout-button").addEventListener("click", function () {
    if (token) {
      token = null;
      sessionStorage.removeItem(tokenKey);
      refresh();
    } else $("login-dialog").showModal();
  });
  $("refresh-button").addEventListener("click", refresh);
  $("add-employee-button").addEventListener("click", function () {
    if (!token) { $("login-dialog").showModal(); return; }
    $("employee-error").textContent = "";
    $("employee-dialog").showModal();
  });
  $("employee-search").addEventListener("input", function (event) {
    var q = event.target.value.trim().toLowerCase();
    renderEmployees(employees.filter(function (p) {
      return [p.first_name, p.last_name, p.email, p.position].join(" ").toLowerCase().indexOf(q) !== -1;
    }));
  });
  document.querySelectorAll("[data-close]").forEach(function (button) {
    button.addEventListener("click", function () { $(button.getAttribute("data-close")).close(); });
  });
  $("employee-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var formElement = event.currentTarget;
    var values = Object.fromEntries(new FormData(formElement).entries());
    values.salary = Number(values.salary);
    values.department_id = values.department_id ? Number(values.department_id) : null;
    api("/api/employees/", { method: "POST", body: JSON.stringify(values) }).then(function () {
      $("employee-dialog").close();
      formElement.reset();
      return refresh();
    }).catch(function (error) { $("employee-error").textContent = error.message; });
  });

  refresh();
  if (!token) $("login-dialog").showModal();
}());
