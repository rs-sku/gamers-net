const PAGE_SIZE = 100;

// Existing screens need complete lists to resolve player links and request statuses.
export async function getAllPages(loadPage, selectItems = data => data) {
    const items = [];
    for (let offset = 0; ; offset += PAGE_SIZE) {
        const data = await loadPage({ limit: PAGE_SIZE, offset });
        const page = selectItems(data);
        if (!Array.isArray(page)) throw new Error('The server returned an invalid list.');
        items.push(...page);
        if (page.length < PAGE_SIZE) return items;
    }
}

export async function getAllPagesResponse(loadPage) {
    try {
        const items = await getAllPages(async pagination => {
            const response = await loadPage(pagination);
            if (!response.ok) throw response;
            return response.json();
        });
        return new Response(JSON.stringify(items), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (error) {
        if (error instanceof Response) return error;
        throw error;
    }
}
