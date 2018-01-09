import re
import wikipedia

def get_movie_details(name):
    print('Searching in wiki for ',name)
    print(wikipedia.search(name))
    title = wikipedia.search(name)[0]
    page = wikipedia.page(title)
    content = page.content
    sections = re.findall('==.*?==', content)

    result = {}
    result['synopsis'] = page.summary
    result['sections'] = []
    result['content'] = {}

    for i in range(len(sections)):
        if sections[i][:3] == '===' and i > 0:
            j = 1
            while sections[i-j][:3] == '===':
                j += 1
            section_name = sections[i-j][3:-2] + ' -> ' + sections[i][4:-2]
        else:
            section_name = sections[i][3:-2]
        result['sections'].append(section_name)
        section_raw_name = sections[i]
        if i < len(sections) - 1:
            result['content'][section_name] = content[content.find(section_raw_name) + len(section_raw_name) : content.find(sections[i + 1])]
        else:
            result['content'][section_name] = content[content.find(section_raw_name) + len(section_raw_name) :]

    return result


#result = get_full_info('Beguiled (2017)')
#print(result)

#print(get_reviews('tt5208216'))
