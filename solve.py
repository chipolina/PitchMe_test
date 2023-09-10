import argparse
import datetime
import json
import logging
from typing import List, Type

from profile_schema import Profile


class DeveloperRole:
    def __init__(self):
        self.role_name = "python_dev"

    def __str__(self):
        return "Python developer"

    def check_profile(self, profile: Profile) -> List:
        logging.info(f"Start checking {profile.first_name} {profile.last_name}")
        FAANG = ["Facebook", "Amazon", "Apple", "Netflix", "Google"]
        reasons = []
        if not any(job_place.company_name in FAANG for job_place in profile.experiences[-3:]):
            reasons.append("Not from a FAANG company")

        recent_positions = [exp.job_title.lower() for exp in profile.experiences[-3:]]
        if recent_positions.count("backend developer") + recent_positions.count("software engineer") < 3:
            reasons.append("Last 3 job positions are not Backend developer or Software engineer")

        total_exp = sum((exp.ends_at - exp.starts_at).days // 365 for exp in profile.experiences if exp.ends_at)
        if total_exp < 8:
            reasons.append("Total experience less that 8 years")

        recent_skills = profile.experiences[-1].skills
        recent_skills = [skill.lower() for skill in recent_skills]
        if "python" not in recent_skills or "c++" not in recent_skills:
            reasons.append("There is no python/c++ experience on the last job")

        if profile.location.city.lower() != "london":
            reasons.append("Located not in London")

        return reasons


class UIRole:
    def __init__(self):
        self.role_name = "ux_designer"

    def __str__(self):
        return "UX Designer"

    def check_profile(self, profile: Profile) -> List:
        logging.info(f"Start checking {profile.first_name} {profile.last_name}")
        reasons = []

        # Check last 2 job positions
        recent_position = [exp.job_title for exp in profile.experiences[-2:]]
        if not any(position in recent_position for position in ["Product designer", "UX-designer", "UI/UX designer"]):
            reasons.append("Last 2 jobs role are not in 'Product designer', 'UX-designer', 'UI/UX designer' ")

        # Check skills
        all_skills = []
        req_skills = ["Figma", "Sketch", "UX-research", "Miro"]
        for job_skills in profile.experiences:
            all_skills.extend(job_skills.skills)
        all_skills = set(all_skills)

        if sum(skill in all_skills for skill in req_skills) < 2:
            reasons.append("There are not 2 necessary skills")

        # Live in Europe
        eu_countries = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                        "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                        "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
                        "Spain", "Sweden"]
        if profile.location.country not in eu_countries:
            reasons.append("Candidate lives not in Europe")

        # Experience on last job more than 2 years

        sorted(profile.experiences, key=lambda exp: exp.starts_at)
        last_job = profile.experiences[-1:][0]
        if last_job.ends_at is None:
            current_datetime = datetime.datetime.now()
            formatted_date = current_datetime.strftime('%Y-%m-%d')
            formatted_date = datetime.datetime.strptime(formatted_date, '%Y-%m-%d').date()
            last_exp = (formatted_date - last_job.starts_at).days
        else:
            last_exp = (last_job.ends_at - last_job.starts_at).days
        if last_exp // 365 < 2:
            reasons.append("Last job experience less than 2 years")

        # Total experience more than 5 years
        total_exp = sum((exp.ends_at - exp.starts_at).days // 365 for exp in profile.experiences if exp.ends_at)
        if total_exp < 5:
            reasons.append("Total experience less that 5 years")

        return reasons


class FilterProfiles:
    def __init__(self):
        self.roles = {
            "python_dev": DeveloperRole(),
            "ux_designer": UIRole()
        }
        logging.basicConfig(filename='script_logs.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self, role_to_search: str, input_file: str) -> None:

        logging.info(f'{"=" * 20}Script started{"=" * 20}')
        logging.info(f'Open input file {input_file}')
        with open(input_file, 'r') as file:
            profiles_data = json.load(file)

        logging.info('Check all profiles for correct schema')
        try:
            profiles = [Profile(**data) for data in profiles_data]
        except:
            logging.error('Error while comparing pydantic schema')
            print("Scripts finished with an error. See the logs")
            raise

        if role_to_search in self.roles:
            logging.info(f'Start looking for {role_to_search} position')
            searching_role = self.roles[role_to_search]
            results = self.filter_profiles(searching_role, profiles)
        else:
            print("Incorrect choice")
            return

        for result in results:
            print(result)
        logging.info(f'{"-" * 20}Script finished{"-" * 20}')

    def filter_profiles(self, role_to_search: Type, profiles: List[Profile]) -> List:
        results = []
        logging.info(f'Start checking for matching {role_to_search} from all candidates')

        for profile in profiles:
            reasons = role_to_search.check_profile(profile)
            if reasons:
                formatted_reasons = '\n'.join(reasons)
                results.append(f"{profile.first_name} {profile.last_name} – False: \n{formatted_reasons}\n{'=' * 100}")
            else:
                results.append(f"{profile.first_name} {profile.last_name} – True\n{'=' * 100}")

        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", required=True, choices=["python_dev", "ux_designer"])
    parser.add_argument("--input", required=True)
    arg = parser.parse_args()

    filter_profiles = FilterProfiles()
    filter_profiles.run(arg.filter, arg.input)


if __name__ == "__main__":
    main()
