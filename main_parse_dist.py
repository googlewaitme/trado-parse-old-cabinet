import logging
from mytradoclub import auth_script
from mytradoclub import parse_dc
from mytradoclub import parse_user


def parse_distributors():
    session = auth_script.auth()
    distributors = parse_dc.parse_dc_by_session(session)
    parse_dc.dumps_dc(distributors, "distibutors.data")


def main():
    unique_club_numbers = []
    distibutors = parse_dc.loads_dc("distibutors.data")
    for dist in distibutors:
        if dist.club_number not in unique_club_numbers:
            unique_club_numbers.append(dist.club_number)
    print(unique_club_numbers)
    session = auth_script.auth()
    for club_number in unique_club_numbers:
        email = parse_user.parse_by_club_number(session, club_number)
        print(club_number, email, sep=',')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
