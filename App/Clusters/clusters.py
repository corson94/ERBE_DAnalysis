from scipy.cluster.vq import kmeans, vq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from tqdm import tqdm


def random_dist(number_of_points=20):
    rng = np.random.default_rng()
    data_rand = rng.random((number_of_points, 2))
    return data_rand

def clusters(data, number_of_clusters=3):
    centroids, d = kmeans(data, number_of_clusters)
    cluster_labels, d2 = vq(data, centroids)
    df = pd.DataFrame(np.vstack((data.T, cluster_labels, d2)).T, columns=['x', 'y', 'labels', 'd2'])\
        .astype({'labels': 'int'})
    df['cen_x'] = [centroids[val][0] for val in df.labels]
    df['cen_y'] = [centroids[val][1] for val in df.labels]
    return df, centroids, d

def plot_clusters(df, centroids):
    fig = px.scatter(df, x=0, y=1, color=2)
    fig.add_traces(list(px.line(centroids, x=0, y=1).select_traces()))
    fig.show(renderer='browser')
    return fig

def lines(df, centroids):
    colors = ['red', 'blue', 'yellow']
    fig = px.scatter(centroids, x=0, y=1)
    x = []
    y = []
    for idx, val in df.iterrows():
        x = [val.x, val.cen_x]
        y = [val.y, val.cen_y]
        # lines_ = pd.DataFrame({'x': x, 'y': y, 'color': df.labels})
        fig.add_trace(go.Scatter(x=x, y=y,
                                 line=go.scatter.Line(color=colors[int(val.labels)]),
                                 showlegend=False))\
            .update_layout(showlegend=False)
    fig.show(renderer='browser')
    # return x, y, df

if __name__ == '__main__':
    distortion = []
    data_rand = random_dist()
    for cluster in tqdm(range(1,10)):
        _, _, d = clusters(data_rand, cluster)
        distortion.append(d)

    fig = px.line(distortion).show(renderer='browser')

    number_of_clusters = int(input("How many clusters is optimum?: "))
    df, centroids, _ = clusters(data_rand, number_of_clusters)
    lines(df, centroids)
