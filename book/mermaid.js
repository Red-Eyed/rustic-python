// Keep the source visible if the optional diagram renderer cannot load.
(async () => {
    const blocks = document.querySelectorAll("code.language-mermaid");
    if (blocks.length === 0) return;
    const { default: mermaid } = await import(
        "https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.esm.min.mjs"
    );
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
    for (const [index, block] of Array.from(blocks).entries()) {
        const { svg } = await mermaid.render(`diagram-${index}`, block.textContent);
        const container = document.createElement("div");
        container.innerHTML = svg;
        block.parentElement.replaceWith(container);
    }
})().catch((error) => console.warn("Diagram source retained:", error));
