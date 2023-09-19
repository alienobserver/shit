import time
import core
import utils

start_time = time.time()
scraper = core.ScrapeArmenPress(num_pages = 5000)
scraper.get_data()
scraper.save()
print(time.time() - start_time)

data = utils.read_data('shit.json')

print(len(data))