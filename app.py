### TEST code version to run from Haroku ###

import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px

#from jupyter_dash import JupyterDash

########### read in data
win_loss_df = pd.read_csv("win_loss_df.csv").sort_values(['wins', 'points_for'], ascending = False)
matchups_df = pd.read_csv("matchups_df.csv")
rosters_df = pd.read_csv("rosters_df.csv")
tm_game_data = pd.read_csv("tm_game_data.csv")
this_week = pd.read_csv("this_week.csv")
this_week_rank = pd.read_csv("this_week.csv")
this_week_rank_avg = pd.read_csv("this_week.csv")

########### define functions
# create agg_week function to sum all stats within the user defined time frame
def agg_week(weekly_boxscore, num_weeks):
    num_weeks_limit = weekly_boxscore["week"].max() - num_weeks
    weekly_boxscore = weekly_boxscore[(weekly_boxscore["week"] <= weekly_boxscore["week"].max()) & \
                                      (weekly_boxscore["week"] > num_weeks_limit)]
    gp_df = weekly_boxscore['team_abv'].value_counts().sort_index().reset_index()    
    weekly_boxscore = weekly_boxscore.groupby(['team_abv']).sum().sort_values(['team_abv']).reset_index()
    weekly_boxscore['gp'] = gp_df['team_abv']
    return weekly_boxscore

# create function to grab team or boxscore stat from prior_weeks dataframe
def get_values_list(prior_weeks_df, team, column):  
    data_list = [prior_weeks_df.loc[prior_weeks_df['team_abv'] == i, column].iloc[0] for i in team.tolist()]
    return np.array(data_list)

# create list of columns to rank in decending order
ascending_false = ['pass_td', 'pass_yrd_per_pass', 'pass_1st_dwn', 'pass_yrd', 'rush_td', 'rush_yrd_per_rush', 
                   'rush_1st_down', 'rush_yrd', 'rec_td', 'rec_yrd_per_tar', 'rec_1st_down', 'rec_yrd_per_gm', 
                   'rec_per_gm', 'def_st_td', 'def_sack', 'def_int', 'def_fbml', 'kck_pts', 'rz_diff', 'to_diff']

# create list of columns to rank in ascending order
ascending_true = ['def_st_td_alw', 'def_st_yrd_alw']

graph_options = ['wins/losses', 'points for/points against']
columns = ['week', 'team_abv', 'oppn', 'QB', 'RB', 'WRTE', 'DEF', 'KICK']
myheading = 'Raytonia Beach Fantasy Football League'
tabtitle='Raytown!'

weekly_points_fig = px.line(matchups_df, x = 'week', y = 'score', 
                            color = 'owner_team_name', 
                            title = 'Scores per Week',
                            hover_name='owner_team_name', 
                            hover_data={'week' : False,
                                        'owner_team_name' : False,
                                        'score' : True
                                        }
                           )

weekly_points_fig.update_xaxes(range=[0.95, 14.05], dtick=1)
weekly_points_fig.layout.update(showlegend=False)

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle


########### Set up the layout
app.layout = html.Div([
    html.H1(myheading),
    dcc.Tabs([
        dcc.Tab(label = 'League Overview', children = [
            html.Div(
                dcc.Dropdown(id = 'graph_option', 
                             options = [{'label' : i, 'value' : i} for i in graph_options],
                             value = 'wins/losses'
                ),
                style = {'width': '15%'}
            ),
            html.Div([
                html.Div([
                    html.H3(),
                    dcc.Graph(id='win_loss_fig')
                ], className="six columns"),

                html.Div([
                    html.H3(),
                    dcc.Graph(id='weekly_points', figure=weekly_points_fig)
                ], className="six columns"),
            ], className="row")
]),
        dcc.Tab(label = 'Weekly NFL Matchup Rankings', children = [
            html.Div([
                html.Div([
                    html.H3(),
                    dcc.Dropdown(id='input_range', 
                                 options = [{'label' : i, 'value' : i} for i in range(1, tm_game_data['week'].max() + 1)],
                                 value = 4
                                )
                ], className="six columns", style = {'width': '10%'})
            ], className="row"),
            html.Div(
                dash_table.DataTable(id = 'rankings_table',
                                     columns=[{"name": i, "id": i} for i in columns],
                                     sort_action='native'
                                    )
            )
        ]),
        dcc.Tab(label = 'Weekly Raytonia Beach Rosters & Predictions', children = [
            html.Div([
                html.Div([
                    html.H3(),
                    dcc.Dropdown(id='week', 
                                 options = [{'label' : i, 'value' : i} for i in rosters_df['week'].unique()],
                                 value = 1
                                )
                ], className="six columns", style = {'width': '5%'}),
                html.Div([
                    html.H3(),
                    dcc.Dropdown(id='owner_team', 
                                 options = [{'label' : i, 'value' : i} for i in rosters_df['owner_team'].unique()],
                                 value = 'Happy Rock Homewreckers'
                                )
                ], className="six columns", style = {'width': '25%'}),
            ], className="row"),    
            html.Div(
                dash_table.DataTable(id = 'roster_table',
                                     columns=[{"name": i, "id": i} for i in rosters_df.columns]
                                    )
            )            
        ])
])
])

@app.callback(
    Output('win_loss_fig', 'figure'),
    [Input('graph_option', 'value')
    ])

def update_graph(column_options):
    if column_options == 'wins/losses':
        win_bars = go.Bar(x=win_loss_df['owner_team_name'], y=win_loss_df['wins'],
                          base=0,
                          marker_color='green',
                          name='Wins',
                          hoverinfo='y'
                         )

        loss_bars = go.Bar(x=win_loss_df['owner_team_name'], y=win_loss_df['losses'],
                           base= -1 * win_loss_df['losses'].astype('int'),
                           text = 1 * win_loss_df['losses'].astype('int'),
                           marker_color='red',
                           name='Losses',
                           hoverinfo='text'
                          )

        win_loss_data = [win_bars, loss_bars]

        win_loss_layout = go.Layout(barmode = 'overlay',
                                    hovermode = 'x',
                                    title = 'Wins/Losses',
                                    yaxis = dict(tickvals = [10, 5, 0, -5, -10],
                                                 ticktext = [10, 5, 0, 5, 10]
                                                )
                                   )


        win_loss_fig = go.Figure(data=win_loss_data, layout=win_loss_layout)
    else:
        win_bars = go.Bar(x=win_loss_df['owner_team_name'], y=win_loss_df['points_for'],
                          base=0,
                          marker_color='green',
                          name='points_for',
                          hoverinfo='y'
                         )

        loss_bars = go.Bar(x=win_loss_df['owner_team_name'], y=win_loss_df['points_against'],
                           base= -1 * win_loss_df['points_against'].astype('int'),
                           text = 1 * win_loss_df['points_against'].astype('int'),
                           marker_color='red',
                           name='points_against',
                           hoverinfo='text'
                          )

        win_loss_data = [win_bars, loss_bars]

        win_loss_layout = go.Layout(barmode = 'overlay',
                                    hovermode = 'x',
                                    title = 'points_for/points_against',
                                    yaxis = dict(tickvals=[3000, 2000, 1000, 0, -1000, -2000, -3000], 
                                                 ticktext = [3000, 2000, 1000, 0, 1000, 2000, 3000]
                                                )
                                   )


        win_loss_fig = go.Figure(data=win_loss_data, layout=win_loss_layout)
        
    return win_loss_fig

@app.callback(
    Output('roster_table', 'data'),
    [Input('week', 'value'),
     Input('owner_team', 'value')
    ])

def update_table(week, team):
    updated_df = rosters_df.loc[(rosters_df['week'] == week) & (rosters_df['owner_team'] == team)].sort_values('slot_id')
    return updated_df.to_dict(orient='records')

@app.callback(
    Output('rankings_table', 'data'),
    [Input('input_range', 'value')
    ])

def update_table(num_weeks):
    prior_weeks = agg_week(tm_game_data, num_weeks)

    # aggregate qb stats
    prior_weeks['pass_td_per_gm'] = prior_weeks['pass_tds'] / prior_weeks['gp']
    prior_weeks['pass_td_alw_per_gm'] = prior_weeks['pass_tds_alw'] / prior_weeks['gp']
    prior_weeks['pass_yrd_per_gm'] = prior_weeks['tot_yrds_pass'] / prior_weeks['gp']
    prior_weeks['pass_yrd_alw_per_gm'] = prior_weeks['tot_yrds_pass_alw'] / prior_weeks['gp']
    prior_weeks['pass_yrd_per_pass'] = prior_weeks['tot_yrds_pass'] / prior_weeks['pass_att']
    prior_weeks['pass_yrd_alw_per_pass_alw'] = prior_weeks['tot_yrds_pass_alw'] / prior_weeks['pass_att_alw']
    prior_weeks['pass_1st_down_per_gm'] = prior_weeks['1st_dwn_pass'] / prior_weeks['gp']
    prior_weeks['pass_1st_down_alw_per_gm'] = prior_weeks['1st_dwn_pass_alw'] / prior_weeks['gp']

    # aggregate rb stats
    prior_weeks['rush_td_per_gm'] = prior_weeks['rush_tds'] / prior_weeks['gp']
    prior_weeks['rush_td_alw_per_gm'] = prior_weeks['rush_tds_alw'] / prior_weeks['gp']
    prior_weeks['rush_yrd_per_gm'] = prior_weeks['tot_rush_yrds'] / prior_weeks['gp']
    prior_weeks['rush_yrd_alw_per_gm'] = prior_weeks['tot_rush_yrds_alw'] / prior_weeks['gp']
    prior_weeks['rush_yrd_per_rush'] = prior_weeks['tot_rush_yrds'] / prior_weeks['rush_att']
    prior_weeks['rush_yrd_alw_per_rush_alw'] = prior_weeks['tot_rush_yrds_alw'] / prior_weeks['rush_att_alw']
    prior_weeks['rush_1st_down_per_gm'] = prior_weeks['1st_dwn_rush'] / prior_weeks['gp']
    prior_weeks['rush_1st_down_alw_per_gm'] = prior_weeks['1st_dwn_rush_alw'] / prior_weeks['gp']

    # aggregate wr/te stats
    prior_weeks['rec_yrd_per_gm'] = prior_weeks['tot_rec_yrds'] / prior_weeks['gp']
    prior_weeks['rec_yrd_alw_per_gm'] = prior_weeks['tot_rec_yrds_alw'] / prior_weeks['gp']
    prior_weeks['rec_yrd_per_tar'] = prior_weeks['tot_rec_yrds'] / prior_weeks['rec_targets']
    prior_weeks['rec_yrd_alw_per_tar_alw'] = prior_weeks['tot_rec_yrds_alw'] / prior_weeks['rec_targets_alw']
    prior_weeks['rec_tar_per_gm'] = prior_weeks['rec_targets'] / prior_weeks['gp']
    prior_weeks['rec_tar_alw_per_gm'] = prior_weeks['rec_targets_alw'] / prior_weeks['gp']
    prior_weeks['rec_per_gm'] = prior_weeks['tot_rec'] / prior_weeks['gp']
    prior_weeks['rec_alw_per_gm'] = prior_weeks['tot_rec_alw'] / prior_weeks['gp']

    # aggregate def stats
    prior_weeks['def_st_td_per_gm'] = (prior_weeks['def_tds'] + prior_weeks['kick_ret_tds'] + prior_weeks['punt_ret_tds']) / \
                                       prior_weeks['gp']
    prior_weeks['def_st_td_alw_per_gm'] = (prior_weeks['def_tds_alw'] + prior_weeks['kick_ret_tds_alw'] + \
                                           prior_weeks['punt_ret_tds_alw']) / prior_weeks['gp']
    prior_weeks['fumble_per_gm'] = prior_weeks['fumble_rec'] / prior_weeks['gp']
    prior_weeks['fumble_lost_per_gm'] = prior_weeks['fumble_lost'] / prior_weeks['gp']
    prior_weeks['int_per_gm'] = prior_weeks['def_ints'] / prior_weeks['gp']
    prior_weeks['int_alw_per_gm'] = prior_weeks['def_ints_alw'] / prior_weeks['gp']
    prior_weeks['sacks_per_gm'] = prior_weeks['tot_sck'] / prior_weeks['gp']
    prior_weeks['sacks_taken_per_gm'] = prior_weeks['sacks_taken'] / prior_weeks['gp']

    # aggregate kick points stats
    prior_weeks['kck_pts_per_gm'] = prior_weeks['kick_pts'] / prior_weeks['gp']
    prior_weeks['kck_pts_alw_per_gm'] = prior_weeks['kick_pts_alw'] / prior_weeks['gp']

    # aggregate kick & punt returns stats
    prior_weeks['return_yrds_per_gm'] = (prior_weeks['kick_ret_yrds'] + prior_weeks['punt_ret_yrds']) / prior_weeks['gp']
    prior_weeks['return_yrds_alw_per_gm'] = (prior_weeks['kick_ret_yrds_alw'] + prior_weeks['punt_ret_yrds_alw']) / \
                                            prior_weeks['gp']
    
    # qb
    # multiply how many TDs thrown per game by team and how many passing TDs allowed per game by opponent
    this_week['pass_td'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'pass_td_per_gm') * 
                                     get_values_list(prior_weeks, this_week['oppn'], 'pass_td_alw_per_gm'))

    # multiply how many yards per pass by team and how many yards per pass allowed by opponent
    this_week['pass_yrd_per_pass'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'pass_yrd_per_pass') * 
                                               get_values_list(prior_weeks, this_week['oppn'], 'pass_yrd_alw_per_pass_alw'))

    # multiply how many passing 1st downs per game by team and how many passing 1st downs per game allowed by opponent
    this_week['pass_1st_dwn'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'pass_1st_down_per_gm') * 
                                          get_values_list(prior_weeks, this_week['oppn'], 'pass_1st_down_alw_per_gm'))

    # multiply passing yards per game by team and passing yards per game allowed by opponent
    this_week['pass_yrd'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'pass_yrd_per_gm') * 
                                      get_values_list(prior_weeks, this_week['oppn'], 'pass_yrd_alw_per_gm'))

    # rb
    # multiply rushing TDs per game by team and rushing TDs allowed per game by opponent
    this_week['rush_td'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rush_td_per_gm') * 
                                     get_values_list(prior_weeks, this_week['oppn'], 'rush_td_alw_per_gm'))

    # multiply how many yards per rush by team and how many yards per rush allowed by opponent
    this_week['rush_yrd_per_rush'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rush_yrd_per_rush') * 
                                               get_values_list(prior_weeks, this_week['oppn'], 'rush_yrd_alw_per_rush_alw'))

    # multiply how many rushing 1st downs per game by team and how many rushing 1st downs per game allowed by opponent
    this_week['rush_1st_down'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rush_1st_down_per_gm') * 
                                           get_values_list(prior_weeks, this_week['oppn'], 'rush_1st_down_alw_per_gm'))

    # multiply rushing yards per game by team and rushing yards per game allowed by opponent
    this_week['rush_yrd'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rush_yrd_per_gm') * 
                                      get_values_list(prior_weeks, this_week['oppn'], 'rush_yrd_alw_per_gm'))

    # wr
    # multiply passing TDs per game by team and passing TDs allowed per game by opponent
    this_week['rec_td'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'pass_td_per_gm') * 
                                    get_values_list(prior_weeks, this_week['oppn'], 'pass_td_alw_per_gm'))

    # multiply receiving yards per game by team and receiving yards per game allowed by opponent
    this_week['rec_yrd_per_gm'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rec_yrd_per_gm') * 
                                            get_values_list(prior_weeks, this_week['oppn'], 'rec_yrd_alw_per_gm'))

    # multiply receiving yards per target by team and receiving yards per target allowed by opponent
    this_week['rec_yrd_per_tar'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rec_yrd_per_tar') * 
                                             get_values_list(prior_weeks, this_week['oppn'], 'rec_yrd_alw_per_tar_alw'))

    # multiply receptions per game by team and receptions per game allowed by opponent
    this_week['rec_per_gm'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'rec_per_gm') * 
                                        get_values_list(prior_weeks, this_week['oppn'], 'rec_alw_per_gm'))

    # multiply how many receiving 1st downs per game by team and how many receiving 1st downs per game allowed by opponent
    this_week['rec_1st_down'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'pass_1st_down_per_gm') * 
                                          get_values_list(prior_weeks, this_week['oppn'], 'pass_1st_down_alw_per_gm'))

    # def
    # multiply def and st TDs per game by team and def and st TDs allowed per game by opponent
    this_week['def_st_td'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'def_st_td_per_gm') * 
                                       get_values_list(prior_weeks, this_week['oppn'], 'def_st_td_alw_per_gm'))

    # multiply def sacks per game by team and sacks taken per game by opponent
    this_week['def_sack'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'sacks_per_gm') * 
                                      get_values_list(prior_weeks, this_week['oppn'], 'sacks_taken_per_gm'))

    # multiply def interceptions per game by team and def interceptions allowed per game by opponent
    this_week['def_int'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'int_per_gm') * 
                                     get_values_list(prior_weeks, this_week['oppn'], 'int_alw_per_gm'))

    # multiply def fumble recoveries per game by team and fumbles lost per game by opponent
    this_week['def_fbml'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'fumble_per_gm') * 
                                      get_values_list(prior_weeks, this_week['oppn'], 'fumble_lost_per_gm'))

    # multiply passing/rushing/def/st TDs allowed per game by team and passing/rushing/def/st TDs per game by opponent
    this_week['def_st_td_alw'] = pd.Series((get_values_list(prior_weeks, this_week['team_abv'], 'pass_td_alw_per_gm') +
                                            get_values_list(prior_weeks, this_week['team_abv'], 'rush_td_alw_per_gm') + 
                                            get_values_list(prior_weeks, this_week['team_abv'], 'def_st_td_alw_per_gm')) * 
                                            (get_values_list(prior_weeks, this_week['oppn'], 'pass_td_per_gm') + 
                                            get_values_list(prior_weeks, this_week['oppn'], 'rush_td_per_gm') + 
                                            get_values_list(prior_weeks, this_week['oppn'], 'def_st_td_per_gm')))

    # multiply passing/rushing/return yards allowed per game by team and passing/rushing/return yards per game by opponent
    this_week['def_st_yrd_alw'] = pd.Series((get_values_list(prior_weeks, this_week['team_abv'], 'pass_yrd_alw_per_gm') +
                                             get_values_list(prior_weeks, this_week['team_abv'], 'rush_yrd_alw_per_gm') + 
                                             get_values_list(prior_weeks, this_week['team_abv'], 'return_yrds_alw_per_gm')) * 
                                             (get_values_list(prior_weeks, this_week['oppn'], 'pass_yrd_per_gm') + 
                                             get_values_list(prior_weeks, this_week['oppn'], 'rush_yrd_per_gm') + 
                                             get_values_list(prior_weeks, this_week['oppn'], 'return_yrds_per_gm')))

    # st
    # multiply kick points per game by team and kick points allowed per game by opponent
    this_week['kck_pts'] = pd.Series(get_values_list(prior_weeks, this_week['team_abv'], 'kck_pts_per_gm') * 
                                     get_values_list(prior_weeks, this_week['oppn'], 'kck_pts_alw_per_gm'))

    # misc
    # calculate redzone differential
    # (conversions divided attempts) minus the inverse (1 minus allowed conversions divided by allowed attempts)
    this_week['rz_diff'] = pd.Series((get_values_list(prior_weeks, this_week['team_abv'], 'redzone_con') /
                                     get_values_list(prior_weeks, this_week['team_abv'], 'redzone_att')) -
                                     (1 - get_values_list(prior_weeks, this_week['oppn'], 'redzone_con_alw') /
                                     get_values_list(prior_weeks, this_week['oppn'], 'redzone_att_alw')))

    # calculate turnover differential
    # (interceptions plus fumbles) minus opponent's (interceptions thrown plus fumbles lost)
    this_week['to_diff'] = pd.Series((get_values_list(prior_weeks, this_week['team_abv'], 'def_ints') +
                                     get_values_list(prior_weeks, this_week['team_abv'], 'fumble_rec')) -
                                     (get_values_list(prior_weeks, this_week['oppn'], 'int_thrown') +
                                     get_values_list(prior_weeks, this_week['oppn'], 'fumble_lost')))
    
    # rank all columns in ascending_false
    for i in ascending_false:
        this_week_rank[i] = this_week[i].rank(method='average', ascending = False)

    # rank all columns in ascending_false
    for i in ascending_true:
        this_week_rank[i] = this_week[i].rank(method='average', ascending = True)
    
    # add "@" to oppn column since all opponents are the home teams due to how the schedule is scraped from ESPN
    this_week_rank_avg.loc[this_week_rank_avg['home'] == False, 'oppn'] = '@' + this_week_rank_avg['oppn'].astype(str)
    this_week_rank_avg.loc[this_week_rank_avg['home'] == True, 'team_abv'] = '@' + this_week_rank_avg['team_abv'].astype(str)

    # group by QB, RB, WR/TE, DEF, and ST using row means
    this_week_rank_avg['QB'] = this_week_rank.iloc[:, [4, 5, 6, 7, 22, 23]].mean(axis=1)
    this_week_rank_avg['RB'] = this_week_rank.iloc[:, [8, 9, 10, 11, 22, 23]].mean(axis=1)
    this_week_rank_avg['WRTE'] = this_week_rank.iloc[:, [12, 13, 14, 15, 16, 22, 23]].mean(axis=1)
    this_week_rank_avg['DEF'] = this_week_rank.iloc[:, [17, 18, 19, 20, 22, 23, 24, 25]].mean(axis=1)
    this_week_rank_avg['KICK'] = this_week_rank.iloc[:, [21, 22, 23]].mean(axis=1)
    
    sorted_df = this_week_rank_avg[['week', 'team_abv', 'oppn', 'QB', 'RB', 'WRTE', 'DEF', 'KICK']].round({'QB': 1, 'RB': 1, 'WRTE': 1, 'DEF': 1, 'KICK': 1})

    return sorted_df.to_dict(orient='records')

if __name__ == '__main__':
    app.run_server()
    
#if __name__ == '__main__':
#    app.run_server(mode='external')