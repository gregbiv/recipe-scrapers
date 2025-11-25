import re

from ._abstract import AbstractScraper
from ._utils import get_minutes

class HelloFresh(AbstractScraper):
    @classmethod
    def host(cls, domain="com"):
        return f"hellofresh.{domain}"

    def cook_time(self):
        script_tag = self.soup.find("script", {"id": "__NEXT_DATA__"})
        if script_tag:
            script_content = script_tag.string
            total_time_match = re.search(r'"totalTime":"(PT\d+M)"', script_content)
            if total_time_match:
                total_time_str = total_time_match.group(1)
                return get_minutes(total_time_str)

    def prep_time(self):
        script_tag = self.soup.find("script", {"id": "__NEXT_DATA__"})
        if script_tag:
            script_content = script_tag.string
            prep_time_match = re.search(r'"prepTime":"(PT\d+M)"', script_content)
            if prep_time_match:
                prep_time_str = prep_time_match.group(1)
                return get_minutes(prep_time_str)

    # Note: HelloFresh uses the 'totalTime' metadata field to represent only the cook time.
    # To get the actual total time, the 'prepTime' and 'totalTime' (which is the cook time) need to be added.
    def total_time(self):
        prep_time, cook_time = self.prep_time(), self.cook_time()
        if prep_time or cook_time:
            return (prep_time or 0) + (cook_time or 0)

    def instructions(self):
        instructions_list = []
        # Find all instruction steps
        instruction_steps = self.soup.find_all("div", {"data-test-id": "instruction-step"})

        for step in instruction_steps:
            text = ""
            image = None

            # Extract text
            text_container = step.find("span", {"type": "body-md-regular"})
            if text_container:
                paragraphs = text_container.find_all('p')
                text_parts = [p.get_text(strip=True) for p in paragraphs]
                text = "\n".join(text_parts)

            # Extract image
            img_tag = step.find("img")
            if img_tag and img_tag.get("src"):
                image = img_tag["src"]

            if text or image:
                instructions_list.append({"text": text, "image": image})

        return instructions_list
