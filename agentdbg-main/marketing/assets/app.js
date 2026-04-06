(() => {
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const navLinks = document.querySelector("[data-nav-links]");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      const next = !navLinks.classList.contains("is-open");
      navLinks.classList.toggle("is-open", next);
      menuToggle.setAttribute("aria-expanded", String(next));
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  document.querySelectorAll("[data-faq-button]").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".faq-item");
      if (!item) return;
      const isOpen = item.getAttribute("data-open") === "true";
      item.setAttribute("data-open", isOpen ? "false" : "true");
      button.setAttribute("aria-expanded", String(!isOpen));
    });
  });

  document.querySelectorAll("[data-copy-value]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = button.getAttribute("data-copy-value");
      if (!value || !navigator.clipboard) return;

      try {
        await navigator.clipboard.writeText(value);
        const original = button.textContent;
        button.textContent = "Copied";
        setTimeout(() => {
          button.textContent = original;
        }, 1200);
      } catch (_) {
        // Ignore clipboard errors to avoid interrupting navigation.
      }
    });
  });

  const blogSearch = document.querySelector("[data-blog-search]");
  const blogCards = Array.from(document.querySelectorAll("[data-blog-card]"));
  const blogCount = document.querySelector("[data-blog-count]");
  const blogTagButtons = Array.from(document.querySelectorAll("[data-blog-tag]"));

  if (blogSearch && blogCards.length) {
    let activeTag = "all";

    const updateBlogFilters = () => {
      const query = blogSearch.value.trim().toLowerCase();
      let visibleCount = 0;

      blogCards.forEach((card) => {
        const tags = (card.getAttribute("data-tags") || "")
          .split(",")
          .map((tag) => tag.trim().toLowerCase())
          .filter(Boolean);
        const title = card.getAttribute("data-title") || "";
        const excerpt = card.getAttribute("data-excerpt") || "";

        const matchesTag = activeTag === "all" || tags.includes(activeTag);
        const matchesQuery =
          !query || title.includes(query) || excerpt.includes(query) || tags.join(" ").includes(query);
        const isVisible = matchesTag && matchesQuery;

        card.hidden = !isVisible;
        if (isVisible) visibleCount += 1;
      });

      if (blogCount) {
        blogCount.textContent = `${visibleCount} article${visibleCount === 1 ? "" : "s"} shown`;
      }
    };

    blogTagButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const nextTag = (button.getAttribute("data-blog-tag") || "all").toLowerCase();
        activeTag = nextTag;
        blogTagButtons.forEach((item) => {
          item.classList.toggle(
            "is-active",
            (item.getAttribute("data-blog-tag") || "").toLowerCase() === activeTag
          );
        });
        updateBlogFilters();
      });
    });

    blogSearch.addEventListener("input", updateBlogFilters);
    updateBlogFilters();
  }

  const tocLinks = Array.from(document.querySelectorAll("[data-toc-link]"));
  if (tocLinks.length) {
    const sections = tocLinks
      .map((link) => {
        const href = link.getAttribute("href") || "";
        if (!href.startsWith("#")) return null;
        return document.querySelector(href);
      })
      .filter(Boolean);

    const setActiveTocLink = () => {
      let activeIndex = 0;
      sections.forEach((section, idx) => {
        const top = section.getBoundingClientRect().top;
        if (top <= 140) activeIndex = idx;
      });

      tocLinks.forEach((link, idx) => {
        link.classList.toggle("is-active", idx === activeIndex);
      });
    };

    window.addEventListener("scroll", setActiveTocLink, { passive: true });
    setActiveTocLink();
  }
})();
