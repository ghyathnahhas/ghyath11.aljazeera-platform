/* ===== منصة جامعة الجزيرة الخاصة - JavaScript ===== */
document.addEventListener("DOMContentLoaded", function() {
    initParticles();
    initSidebar();
    initHeaderScroll();
    initCounters();
    initDropdowns();
});

/* ===== جزيئات الخلفية ===== */
function initParticles() {
    var container = document.getElementById("particles");
    if (!container) return;
    for (var i = 0; i < 20; i++) {
        var p = document.createElement("div");
        p.className = "particle";
        var size = Math.random() * 60 + 20;
        p.style.width = size + "px";
        p.style.height = size + "px";
        p.style.left = Math.random() * 100 + "%";
        p.style.animationDuration = (Math.random() * 20 + 15) + "s";
        p.style.animationDelay = (Math.random() * 10) + "s";
        container.appendChild(p);
    }
}

/* ===== القائمة الجانبية ===== */
function initSidebar() {
    var toggle = document.getElementById("sidebarToggle");
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebarOverlay");
    var close = document.getElementById("sidebarClose");
    if (!toggle || !sidebar) return;
    toggle.addEventListener("click", function() {
        sidebar.classList.add("open");
        if (overlay) overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    });
    function closeSidebar() {
        sidebar.classList.remove("open");
        if (overlay) overlay.classList.remove("active");
        document.body.style.overflow = "";
    }
    if (close) close.addEventListener("click", closeSidebar);
    if (overlay) overlay.addEventListener("click", closeSidebar);

    var dropdownParents = sidebar.querySelectorAll(".sidebar-dropdown-parent > a");
    dropdownParents.forEach(function(link) {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            this.parentElement.classList.toggle("open");
        });
    });
}

/* ===== تمرير الشريط العلوي ===== */
function initHeaderScroll() {
    var header = document.getElementById("mainHeader");
    if (!header) return;
    window.addEventListener("scroll", function() {
        if (window.scrollY > 50) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }
    });
}

/* ===== عداد الأرقام ===== */
function initCounters() {
    var counters = document.querySelectorAll(".stat-number[data-count]");
    if (counters.length === 0) return;
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    counters.forEach(function(c) { observer.observe(c); });
}

function animateCounter(el) {
    var target = parseInt(el.getAttribute("data-count"));
    var current = 0;
    var step = Math.max(1, Math.ceil(target / 60));
    var timer = setInterval(function() {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = current;
    }, 30);
}

/* ===== القوائم المنسدلة للهاتف ===== */
function initDropdowns() {
    if (window.innerWidth > 768) return;
    var dropdownToggles = document.querySelectorAll(".has-dropdown > .dropdown-toggle");
    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener("click", function(e) {
            e.preventDefault();
            var menu = this.nextElementSibling;
            if (menu) {
                var isOpen = menu.style.display === "block";
                document.querySelectorAll(".dropdown-menu").forEach(function(m) { m.style.display = "none"; });
                if (!isOpen) menu.style.display = "block";
            }
        });
    });
}

/* ===== نافذة تأكيد الحذف ===== */
function confirmDelete(url) {
    var modal = document.getElementById("deleteModal");
    var form = document.getElementById("deleteForm");
    if (modal && form) {
        form.action = url;
        modal.classList.add("active");
    }
}

function closeDeleteModal() {
    var modal = document.getElementById("deleteModal");
    if (modal) modal.classList.remove("active");
}

document.addEventListener("click", function(e) {
    var modal = document.getElementById("deleteModal");
    if (e.target === modal) closeDeleteModal();
});

document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") closeDeleteModal();
});

/* ===== تمرير سلس ===== */
function scrollToColleges() {
    var el = document.getElementById("colleges-section");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ===== إغلاق الرسائل المنبثقة تلقائياً ===== */
setTimeout(function() {
    var flashes = document.querySelectorAll(".flash-message");
    flashes.forEach(function(f) {
        setTimeout(function() {
            f.style.opacity = "0";
            f.style.transform = "translateY(-10px)";
            setTimeout(function() { f.remove(); }, 300);
        }, 5000);
    });
}, 100);
