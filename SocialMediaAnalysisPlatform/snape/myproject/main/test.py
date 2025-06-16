def create_or_view_visualization(request):
    try:
        # Retrieve uploaded data
        uploaded_data = request.session.get('uploaded_data', [])
        headers = request.session.get('uploaded_headers', [])

        if not uploaded_data or not headers:
            messages.error(request, "No data available for visualization.")
            return redirect('upload_csv_or_xlsx')

        # Step 1: Build the Graph
        G = nx.Graph()
        max_edges_per_node = 5  # Limit the maximum edges per node

        for row in uploaded_data:
            row_nodes = []
            for header in headers:
                value = row.get(header)
                # Filter out noisy or invalid values
                if value and isinstance(value, str) and len(value) < 50 and value not in ['null', 'None', 'nan', '-', '']:
                    if 'http' in value or 'timestamp' in header.lower():  # Exclude URLs and timestamps
                        continue
                    row_nodes.append(value)

            # Add edges while limiting connections
            for i in range(len(row_nodes)):
                for j in range(i + 1, len(row_nodes)):
                    if G.degree(row_nodes[i]) < max_edges_per_node and G.degree(row_nodes[j]) < max_edges_per_node:
                        G.add_edge(row_nodes[i], row_nodes[j])

        # Step 2: Filter for Large Graphs
        if G.number_of_nodes() > 200:  # Keep important nodes
            nodes_to_keep = [node for node, degree in G.degree() if degree >= 3]
            G = G.subgraph(nodes_to_keep).copy()

        # Step 3: Dynamically Layout the Graph
        layout_style = request.GET.get('layout', 'kamada_kawai')
        if layout_style == 'spring':
            pos = nx.spring_layout(G, k=0.8, seed=42)  # "k" adjusts node spacing
        elif layout_style == 'circular':
            pos = nx.circular_layout(G)
        else:
            pos = nx.kamada_kawai_layout(G)

        # Step 4: Highlight Important Nodes
        degree_threshold = 5
        high_degree_nodes = [node for node, degree in G.degree() if degree > degree_threshold]
        node_colors = ['orange' if node in high_degree_nodes else 'skyblue' for node in G.nodes]
        node_sizes = [max(300, min(degree * 50, 1000)) for _, degree in G.degree()]

        # Step 5: Plot the Graph
        plt.figure(figsize=(16, 12))
        nx.draw(G, pos, with_labels=True,
                node_color=node_colors,
                node_size=node_sizes,
                edge_color="gray",
                font_size=8, alpha=0.7)

        # Save the graph image as Base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Render the visualization
        return render(request, 'main/view_visualization.html', {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'visualization_image': f"data:image/png;base64,{img_base64}"
        })

    except Exception as e:
        messages.error(request, f"Error creating visualization: {str(e)}")
        return redirect('upload_csv_or_xlsx')
