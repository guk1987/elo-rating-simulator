import pandas as pd
import random
from random import choices
import warnings
warnings.filterwarnings("ignore")


# 유저 생성 (id, name, 실제 실력 기반 고정 elo, 게임에 반영된 elo)
def create_user(create_max_user, start_elo_point, start_k):
    users = pd.DataFrame(
        {'id': [i for i in range(1, create_max_user+1)],
         'real_elo': [random.randint(800, 1500) for i in range(1, create_max_user+1)],
         'game_elo': [start_elo_point for i in range(1, create_max_user+1)],
         'win': [0 for i in range(1, create_max_user+1)],
         'draw': [0 for i in range(1, create_max_user+1)],
         'lose': [0 for i in range(1, create_max_user+1)],
         'game_cnt': [0 for i in range(1, create_max_user+1)],
         'tier': ['bronze'for i in range(1, create_max_user+1)],
         'tier_k': [start_k for i in range(1, create_max_user+1)]
         }
    )
    return users


# 생성된 유저중에서 두 개의 팀을 가져옴
def get_team(users, sample_size):
    sample_users = users.sample(sample_size)
    a_team = sample_users.head(int(sample_size/2))
    b_team = sample_users.tail(int(sample_size/2))
    return a_team, b_team


# 각 팀의 평균 elo를 구함
def get_team_elo_point(a_team, b_team, what_elo):
    a_team_elo = a_team[what_elo].mean()
    b_team_elo = b_team[what_elo].mean()

    return a_team_elo, b_team_elo


# 각 팀의 승률을 구함
def get_win_expectation(a_team_elo, b_team_elo):
    win_e = 1/(1+10**((b_team_elo-a_team_elo)/600))
    a_team_win_e = win_e
    b_team_win_e = 1-win_e
    return a_team_win_e, b_team_win_e


# 티어 업데이트 (게임 플레이가 있는 유저 기준으로 % 끊어서 계산)
def update_tier(users):

    playing_user = users[users['game_cnt'] > 0]
    playing_user = playing_user.sort_values(
        by='game_elo', ascending=False, ignore_index=True)

    playing_user_cnt = playing_user.id.count()
    bronze_cnt = int(playing_user_cnt * tier['bronze'])
    silver_cnt = int(playing_user_cnt * tier['silver'])
    gold_cnt = int(playing_user_cnt * tier['gold'])
    platinum_cnt = int(playing_user_cnt * tier['platinum'])
    diamond_cnt = int(playing_user_cnt * tier['diamond'])
    master_cnt = int(playing_user_cnt * tier['master'])

    sum_cnt = bronze_cnt + silver_cnt + gold_cnt + \
        platinum_cnt + diamond_cnt + master_cnt
    bronze_cnt = bronze_cnt + playing_user_cnt - sum_cnt

    playing_user.iloc[:master_cnt, :]['tier'] = 'master'
    playing_user.iloc[master_cnt:master_cnt +
                      diamond_cnt, :]['tier'] = 'diamond'
    playing_user.iloc[master_cnt+diamond_cnt: master_cnt +
                      diamond_cnt+platinum_cnt, :]['tier'] = 'platinum'
    playing_user.iloc[master_cnt+diamond_cnt+platinum_cnt: master_cnt +
                      diamond_cnt+platinum_cnt+gold_cnt, :]['tier'] = 'gold'
    playing_user.iloc[master_cnt+diamond_cnt+platinum_cnt+gold_cnt: master_cnt +
                      diamond_cnt+platinum_cnt+gold_cnt+silver_cnt, :]['tier'] = 'silver'
    playing_user.iloc[master_cnt+diamond_cnt+platinum_cnt+gold_cnt+silver_cnt: master_cnt +
                      diamond_cnt+platinum_cnt+gold_cnt+silver_cnt+bronze_cnt, :]['tier'] = 'bronze'

    return playing_user


# 티어별로 k 값을 업데이트
def update_k(df_a, tier_k):
    df_a.loc[df_a['tier'] ==
             'master', 'tier_k'] = tier_k['master']
    df_a.loc[df_a['tier'] ==
             'diamond', 'tier_k'] = tier_k['diamond']
    df_a.loc[df_a['tier'] ==
             'platinum', 'tier_k'] = tier_k['platinum']
    df_a.loc[df_a['tier'] == 'gold', 'tier_k'] = tier_k['gold']
    df_a.loc[df_a['tier'] ==
             'silver', 'tier_k'] = tier_k['silver']
    df_a.loc[df_a['tier'] ==
             'bronze', 'tier_k'] = tier_k['bronze']
    return df_a


def update_users(df_a, df_b):
    users_sum = pd.concat([df_a, df_b])
    users = users_sum.drop_duplicates(subset=['id'], keep="last")
    users['game_cnt'] = users['win'] + users['draw'] + users['lose']
    return users
############################################ 시뮬레이션 시작 코드 ############################################


################# 세팅값 #################
create_max_user = 200   # 유저 생성 숫자
start_elo_point = 1200  # 시작 elo 포인트
sample_size = 10  # 팀 생성시 사용되는 유저 수. ex) 10 = 10인방으로 각 팀당 5명 배당
session_cnt = 100  # 세션 수 (시뮬레이션 할 총 게임 수)

# 티어별 인원 %
tier = {
    "master": 0.01,
    "diamond": 0.04,
    "platinum": 0.1,
    "gold": 0.2,
    "silver": 0.3,
    "bronze": 0.35,
}

# 티어별 세팅되는 k 값
tier_k = {
    "master": 20,
    "diamond": 30,
    "platinum": 40,
    "gold": 50,
    "silver": 70,
    "bronze": 100,
}


################# 유저 생성 #################
users = create_user(create_max_user, start_elo_point, tier_k['bronze'])


################# 게임(세션) 돌림 #################
for i in range(session_cnt):

    # 팀 생성
    a_team, b_team = get_team(users, sample_size)

    # 팀 실제 실력 (고정 elo)
    a_team_elo_r, b_team_elo_r = get_team_elo_point(
        a_team, b_team, what_elo='real_elo')

    # 팀 실력 점수 (유동 elo)
    a_team_elo_g, b_team_elo_g = get_team_elo_point(
        a_team, b_team, what_elo='game_elo')

    # 팀 실제 승률
    a_team_win_e_r, b_team_win_e_r = get_win_expectation(
        a_team_elo_r, b_team_elo_r)

    # 팀 점수 계산을 위한 승률
    a_team_win_e_g, b_team_win_e_g = get_win_expectation(
        a_team_elo_g, b_team_elo_g)

    # 게임 매치!!
    # print(f"A팀({a_team_elo_r}점 / 승률 : {a_team_win_e_r*100}%\n                      VS                      \nB팀({b_team_elo_r}점 / 승률 : {b_team_win_e_r*100}%")
    # 0 = 패배 / 1 = 무승부 / 2 = 승리
    # 모두 동일한 확률로 choice
    win_rst = random.choices(range(0, 3), weights=[
        a_team_win_e_r, 0, b_team_win_e_r])

    # 승/무/패 결과 처리
    if win_rst == [0]:  # A팀 승리
        a_team['win'] = a_team['win'] + 1
        b_team['lose'] = b_team['lose'] + 1
        # elo update
        a_team['game_elo'] = a_team['game_elo'] + \
            a_team['tier_k'] * (1 - a_team_win_e_g)
        b_team['game_elo'] = b_team['game_elo'] + \
            b_team['tier_k'] * (0 - b_team_win_e_g)

    elif win_rst == [1]:  # 무승부
        a_team['draw'] = a_team['draw'] + 1
        b_team['draw'] = b_team['draw'] + 1
        # elo update
        a_team['game_elo'] = a_team['game_elo'] + \
            a_team['tier_k'] * (0.5 - a_team_win_e_g)
        b_team['game_elo'] = b_team['game_elo'] + \
            b_team['tier_k'] * (0.5 - b_team_win_e_g)

    elif win_rst == [2]:  # B팀 승리
        a_team['lose'] = a_team['lose'] + 1
        b_team['win'] = b_team['win'] + 1
        # elo update
        a_team['game_elo'] = a_team['game_elo'] + \
            a_team['tier_k'] * (0 - a_team_win_e_g)
        b_team['game_elo'] = b_team['game_elo'] + \
            b_team['tier_k'] * (1 - b_team_win_e_g)

    # A, B팀을 하나로 합침 (users에 업데이트하기 위해)
    teams = a_team.append(b_team)
    # print(teams)

    # users <- teams 정보를 업데이트함 (ELO 점수와 승무패 점수)
    users = update_users(users, teams)

    # 생성한 유저 전체 Users가 아닌 플레이 기록이 있는 유저들만 가지고 Tier 나눔
    playing_user = update_tier(users)

    # 티어별로 계산되는 K값 update
    plying_user = update_k(playing_user, tier_k)

    # 전체 유저 정보가 담긴 users에서도 tier와 tier별 k값을 업데이트 (다음 게임 인원 차출시 사용하기 위해)
    users = update_k(users, tier_k)
    users = update_users(users, playing_user)
################# 한 게임(세션) 종료 #################

# 진행률 표시
    if (i % (session_cnt/100)) == 0:
        print(f'진행률: {int(i / session_cnt * 100)}% ({i} / {session_cnt})')
print("진행률: 100%")

# 최종 결과 값을 excel 파일로 저장
playing_user.to_excel(
    f'elo_createUsers_{create_max_user}_sessionCnt_{session_cnt}_tierK_[{tier_k["master"]},{tier_k["diamond"]},{tier_k["platinum"]},{tier_k["gold"]},{tier_k["silver"]},{tier_k["bronze"]}].xlsx')
